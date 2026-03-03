import logging
import random

from django.contrib.admin import AdminSite
from django.contrib.auth import login as auth_login, get_user_model
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, path
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
logger = logging.getLogger(__name__)

SESSION_KEY = '_admin_pending_phone'
CACHE_KEY_PREFIX = 'admin_sms'


def send_sms_code(phone: str, code: str) -> None:
    """
    SMS yuborish funksiyasi.
    Bu yerni o'z SMS provayderingiz (masalan Eskiz.uz yoki Play Mobile) bilan almashtiring.
    """
    # TODO: Real SMS provider integratsiyasini qo'shing
    # Misol (Eskiz.uz):
    # import requests
    # requests.post('https://notify.eskiz.uz/api/message/sms/send', data={
    #     'mobile_phone': phone,
    #     'message': f'Tasdiqlash kodi: {code}',
    #     'from': '4546',
    # }, headers={'Authorization': f'Bearer {settings.ESKIZ_TOKEN}'})
    print(f"[SMS] Phone: {phone} | Code: {code}")


def _format_phone(phone: str) -> str:
    """998931234567 → +998(93) 123-45-67"""
    if len(phone) == 12 and phone.startswith('998'):
        return f"+998({phone[3:5]}) {phone[5:8]}-{phone[8:10]}-{phone[10:12]}"
    return phone


class CustomAdminSite(AdminSite):

    def get_urls(self):
        custom_urls = [
            path(
                'login/confirm/',
                csrf_protect(never_cache(self.login_confirm_view)),
                name='%s_login_confirm' % self.name,
            ),
        ]
        return custom_urls + super().get_urls()

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        if request.user.is_authenticated and self.has_permission(request):
            return HttpResponseRedirect(reverse('admin:index', current_app=self.name))

        error = None

        if request.method == 'POST':
            from apps.models import User
            raw = request.POST.get('phone', '').strip()
            phone = ''.join(c for c in raw if c.isdigit())

            if not phone:
                error = "Telefon raqamini kiriting."
            else:
                try:
                    user = User.objects.get(phone=phone)
                    if not user.is_admin:
                        error = "Sizda admin huquqi mavjud emas."
                    else:
                        code = str(random.randint(100000, 999999))
                        cache.set(f'{CACHE_KEY_PREFIX}:{phone}', code, timeout=60)
                        send_sms_code(phone, code)
                        # Phone sessionga saqlanadi — URL'da ko'rinmaydi
                        request.session[SESSION_KEY] = phone
                        confirm_url = reverse('admin:admin_login_confirm', current_app=self.name)
                        return HttpResponseRedirect(confirm_url)
                except User.DoesNotExist:
                    error = "Bu telefon raqam bilan foydalanuvchi topilmadi."

        context = {
            **self.each_context(request),
            'title': 'Tizimga kirish',
            'error': error,
        }
        return render(request, 'admin/login.html', context)


    def login_confirm_view(self, request):
        phone = request.session.get(SESSION_KEY, '')

        if not phone:
            return HttpResponseRedirect(reverse('admin:login', current_app=self.name))

        def _render(error=None):
            return render(request, 'admin/login_confirm.html', {
                **self.each_context(request),
                'title': 'Kodni tasdiqlash',
                'phone_display': _format_phone(phone),
                'error': error,
            })

        # GET — faqat forma ko'rsatish
        if request.method == 'GET':
            return _render()

        # POST — kodni tekshirish
        User = get_user_model()
        code_input = request.POST.get('code', '').strip()
        cached_code = cache.get(f'{CACHE_KEY_PREFIX}:{phone}')

        if not cached_code:
            return _render(error="Kod muddati tugagan (1 daqiqa). Iltimos, qaytadan telefon raqam kiriting.")

        if code_input != cached_code:
            return _render(error="Noto'g'ri kod. Qaytadan urinib ko'ring.")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return _render(error="Foydalanuvchi topilmadi.")

        if not user.is_admin:
            return _render(error="Sizda admin huquqi mavjud emas.")

        cache.delete(f'{CACHE_KEY_PREFIX}:{phone}')
        del request.session[SESSION_KEY]
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        auth_login(request, user)
        return HttpResponseRedirect(reverse('admin:index', current_app=self.name))


custom_admin_site = CustomAdminSite(name='admin')

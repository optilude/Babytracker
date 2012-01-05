def is_mobile(info, request):
    return getattr(request, 'mobile', False)
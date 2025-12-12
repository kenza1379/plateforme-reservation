from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('espace/<int:espace_id>/', views.detail_espace, name='detail_espace'),
    path('espaces/categorie/<str:categorie>/', views.espaces_par_categorie, name='espaces_par_categorie'),


    path("mon-compte/", views.mon_compte, name="mon_compte"),
    path("mes-reservations/", views.mes_reservations, name="mes_reservations"),
    path("mes-favoris/", views.mes_favoris, name="mes_favoris"),

    path('mon-compte/security/', views.security_settings, name='security_settings'),
    path('security/change-password/', views.change_password, name='change_password'),

    path('security/logout-session/<str:session_key>/', views.logout_session, name='logout_session'),
    path('security/logout-all/', views.logout_all_sessions, name='logout_all_sessions'),

    path('account/delete/', views.delete_account, name='delete_account'),

    path("mon-compte/payment-methods/", views.payment_methods, name="payment_methods"),
    path("mon-compte/payment-methods/add/", views.add_card, name="add_card"),
    path("mon-compte/payment-methods/delete/<int:card_id>/", views.delete_card, name="delete_card"),
    path("mon-compte/payment-methods/default/<int:card_id>/", views.set_default_card, name="set_default_card"),

    path('reserver/<int:espace_id>/', views.reserver_espace, name='reserver_espace'),

    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:reservation_id>/annuler/', views.cancel_reservation, name='cancel_reservation'),

    path('reservation/<int:reservation_id>/payment/', views.payment_page, name='payment_page'),
    path('reservation/<int:reservation_id>/process-payment/', views.process_payment, name='process_payment'),

    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
    path('toggle-favori/<int:espace_id>/', views.toggle_favori, name='toggle_favori'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

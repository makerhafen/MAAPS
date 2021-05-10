from django.contrib import admin

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
import maaps.views as views

urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'', views.index, name='index'),

    # Point of sale
    path(r'pos/'           , views.pos__index      , name='pos__index'),
    path(r'pos/logout'     , views.pos__logout     , name='pos__logout'),
    path(r'pos/deposit'    , views.pos__deposit    , name='pos__deposit'),
    path(r'pos/payment'    , views.pos__payment    , name='pos__payment'),
    path(r'pos/write_card' , views.pos__write_card , name='pos__write_card'),
    path(r'pos/info'       , views.pos__info       , name='pos__info'),
    path(r'pos/staff_login', views.pos__staff_login, name='pos__staff_login'),
    path(r'pos/staff_login/<user_token>', views.pos__staff_login, name='pos__staff_login_with_parameter'),

    # Machine
    path(r'machine/'                            , views.machine__login_machine    , name='machine__login'),
    path(r'machine/logout'                      , views.machine__logout_machine   , name='machine__logout'),
    path(r'machine/show_session'                , views.machine__show_session     , name='machine__show_session'),
    path(r'machine/login_user'                  , views.machine__login_user       , name='machine__login_user'),
    path(r'machine/login_user/<user_token>'     , views.machine__login_user       , name='machine__login_user_with_parameter'),
    path(r'machine/logout_user'                 , views.machine__logout_user      , name='machine__logout_user'),
    path(r'machine/pay_material'                , views.machine__pay_material     , name='machine__pay_material'),
    path(r'machine/pay_material/<user_token>'   , views.machine__pay_material     , name='machine__pay_material_with_parameter'),
    path(r'machine/rate_machine'                , views.machine__rate_machine     , name='machine__rate_machine'),
    path(r'machine/tutor_required'              , views.machine__tutor_required   , name='machine__tutor_required'),
    path(r'machine/payment_required'            , views.machine__payment_required , name='machine__payment_required'),
    path(r'machine/other_user_pays'             , views.machine__other_user_pays  , name='machine__payment_other_user_pays'),
    path(r'machine/other_user_pays/<user_token>', views.machine__other_user_pays  , name='machine__payment_other_user_pays_with_parameter'),
    path(r'machine/auto_logout'                 , views.machine__auto_logout      , name='machine__auto_logout'),
    path(r'machine/M:<machine_token>'           , views.machine__login_machine    , name='machine__login_with_parameter'),

    # Webinterface
    path('webif/'                         , views.webif__dashboard   , name='webif__dashboard'),
    path('webif/info'                     , views.webif__info   , name='webif__info'),
    path('webif/user/list'                , views.webif__user__list  , name='webif__user__list'),
    path('webif/user/create'              , views.webif__user__create, name='webif__user__create'),
    path('webif/user/show/<int:user_id>'  , views.webif__user__show  , name='webif__user__show'),
    path('webif/user/update/<int:user_id>', views.webif__user__update, name='webif__user__update'),
    path('webif/user/delete/<int:user_id>', views.webif__user__delete, name='webif__user__delete'),
    path('webif/user/haft/<int:user_id>'  , views.webif__user__haftung, name='webif__user__haftung'),
    path('webif/user/create_new_card/<int:user_id>'  , views.webif__user__create_new_card, name='webif__user__create_new_card'),

    path('webif/invoice/list'                 , views.webif__invoice__list, name='webif__invoice__list'),
    path('webif/invoice/show/<int:invoice_id>', views.webif__invoice__show, name='webif__invoice__show'),
    path('webif/invoice/create_select/'              , views.webif__invoice__create_select, name='webif__invoice__create_select'),
    path('webif/invoice/create/<int:user_id>' , views.webif__invoice__create, name='webif__invoice__create'),

      ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


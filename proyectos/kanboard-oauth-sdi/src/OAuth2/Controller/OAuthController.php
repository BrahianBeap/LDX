<?php

namespace Kanboard\Plugin\OAuth2\Controller;

use Kanboard\Controller\OAuthController as BaseOAuthController;

/**
 * Reutiliza el flujo del Core (step1 → redirige a SDI; step2 → valida el
 * state y autentica). Solo cambia el proveedor y el mensaje de error.
 */
class OAuthController extends BaseOAuthController
{
    public function handler()
    {
        // Con sesión iniciada, el Core intentaría "vincular" la cuenta
        // externa, algo que este plugin no usa.
        if ($this->userSession->isLogged()) {
            $this->response->redirect($this->helper->url->to('DashboardController', 'show'));
            return;
        }

        // Sin esto, un retorno de SDI con error y sin código volvería a
        // redirigir a SDI (step1), y podría quedar en un bucle.
        if ($this->request->getStringParam('error') !== '') {
            $this->authenticationFailure('SDI rechazó el ingreso. Probá de nuevo o ingresá con tu contraseña.');
            return;
        }

        $this->step1('SdiAd');
    }

    protected function authenticate($providerName)
    {
        if ($this->authenticationManager->oauthAuthentication($providerName)) {
            $this->redirectAfterLogin();
            return;
        }

        $error = $this->authenticationManager->getProvider($providerName)->getError();
        $this->authenticationFailure($error ?: t('External authentication failed'));
    }
}

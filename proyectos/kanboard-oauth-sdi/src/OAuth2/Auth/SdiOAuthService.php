<?php

namespace Kanboard\Plugin\OAuth2\Auth;

use Kanboard\Core\Base;

/**
 * Cliente del OAuth de SDI. Reproduce lo que hace ADM-TECH (index.php),
 * que es la referencia que funciona:
 *
 * - authorize: solo client_id (sin redirect_uri: SDI usa la URL registrada).
 * - token: POST JSON {client_id, client_secret, code}; la respuesta es
 *   {"status":"success","data":{"access_token":"<JWT>"}}.
 * - los datos del usuario salen del payload del JWT (sub = TPPY, mail, ...).
 *
 * La firma del JWT no se verifica: el token llega directo de SDI por HTTPS
 * con el certificado validado, en un pedido autenticado con el secreto.
 */
class SdiOAuthService extends Base
{
    const AUTHORIZE_URL = 'https://ciberseg.personal.com.py/ad/login/oauth/authorize/';
    const TOKEN_URL = 'https://ciberseg.personal.com.py/ad/login/oauth/access_token';
    const STATE_KEY = 'sdiOAuthState';
    const STATE_TTL = 600;

    public function getAuthorizationUrl()
    {
        $state = $this->token->getToken();
        session_set(self::STATE_KEY, array('value' => $state, 'expires' => time() + self::STATE_TTL));

        return self::AUTHORIZE_URL.'?'.http_build_query(array(
            'client_id' => SDI_OAUTH_CLIENT_ID,
            'state' => $state,
        ));
    }

    /**
     * El retorno solo es válido si este navegador inició el ingreso hace
     * menos de STATE_TTL segundos. Si SDI devuelve el state, además tiene
     * que coincidir. No está confirmado que SDI lo devuelva: si no viene,
     * alcanza con el ingreso pendiente en la sesión (de un solo uso).
     */
    public function isValidateState($state)
    {
        $pending = session_get(self::STATE_KEY);
        session_remove(self::STATE_KEY);

        if (! is_array($pending) || $pending['expires'] < time()) {
            return false;
        }

        return $state === '' || hash_equals($pending['value'], $state);
    }

    /**
     * Canjea el código por el token y devuelve los claims, o array() si falla.
     */
    public function getClaims($code)
    {
        $body = $this->httpClient->postJson(self::TOKEN_URL, array(
            'client_id' => SDI_OAUTH_CLIENT_ID,
            'client_secret' => SDI_OAUTH_CLIENT_SECRET,
            'code' => $code,
        ));

        $response = json_decode($body, true);

        if (! is_array($response) || ($response['status'] ?? '') !== 'success' || empty($response['data']['access_token'])) {
            $this->logger->error('SdiAd: respuesta inesperada del token ('.substr((string) $body, 0, 200).')');
            return array();
        }

        $parts = explode('.', $response['data']['access_token']);

        if (count($parts) !== 3) {
            $this->logger->error('SdiAd: el access_token no es un JWT');
            return array();
        }

        $claims = json_decode(base64_decode(strtr($parts[1], '-_', '+/')), true);

        return is_array($claims) ? $claims : array();
    }
}

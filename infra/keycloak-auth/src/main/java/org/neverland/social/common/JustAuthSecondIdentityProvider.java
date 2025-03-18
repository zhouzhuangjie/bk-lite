package org.neverland.social.common;

import cn.hutool.json.JSONUtil;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.WebApplicationException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.core.UriBuilder;
import me.zhyd.oauth.config.AuthConfig;
import me.zhyd.oauth.model.AuthCallback;
import me.zhyd.oauth.model.AuthResponse;
import me.zhyd.oauth.model.AuthUser;
import me.zhyd.oauth.request.AuthDefaultRequest;
import me.zhyd.oauth.request.AuthRequest;
import org.apache.http.auth.AUTH;
import org.keycloak.OAuth2Constants;
import org.keycloak.OAuthErrorException;
import org.keycloak.broker.oidc.AbstractOAuth2IdentityProvider;
import org.keycloak.broker.oidc.OAuth2IdentityProviderConfig;
import org.keycloak.broker.provider.AuthenticationRequest;
import org.keycloak.broker.provider.BrokeredIdentityContext;
import org.keycloak.broker.provider.IdentityBrokerException;
import org.keycloak.broker.social.SocialIdentityProvider;
import org.keycloak.events.Errors;
import org.keycloak.events.EventBuilder;
import org.keycloak.events.EventType;
import org.keycloak.models.Constants;
import org.keycloak.models.KeycloakSession;
import org.keycloak.models.RealmModel;
import org.keycloak.services.ErrorPage;
import org.keycloak.services.messages.Messages;
import org.keycloak.sessions.AuthenticationSessionModel;

import java.util.function.Function;

public class JustAuthSecondIdentityProvider
        extends AbstractOAuth2IdentityProvider<JustAuthIdentityProviderConfig>
        implements SocialIdentityProvider<JustAuthIdentityProviderConfig> {

    public final String DEFAULT_SCOPES = "default";
    //OAuth2IdentityProviderConfig
    public final AuthConfig AUTH_CONFIG;
    public final Function<AuthConfig, AuthDefaultRequest> authToReqFunc;

    public JustAuthSecondIdentityProvider(KeycloakSession session, JustAuthIdentityProviderConfig config) {
        super(session, config);
        this.AUTH_CONFIG = JustAuthKey.getAuthConfig(config);
        this.authToReqFunc = config.getAuthToReqFunc();
    }

    @Override
    protected UriBuilder createAuthorizationUrl(AuthenticationRequest request) {
        String redirectUri = request.getRedirectUri();
        AuthRequest authRequest = getAuthRequest(AUTH_CONFIG, redirectUri);
        String uri = authRequest.authorize(request.getState().getEncoded());
        return UriBuilder.fromUri(uri);
    }

    private AuthRequest getAuthRequest(AuthConfig authConfig, String redirectUri) {
        authConfig.setRedirectUri(redirectUri);
        return authToReqFunc.apply(authConfig);
    }

    @Override
    public Object callback(RealmModel realm, AuthenticationCallback callback, EventBuilder event) {
        logger.infof("handler callback: start");
        return new EndpointCurrent(callback, realm, event, this);
    }

    protected class EndpointCurrent extends Endpoint {

        private final JustAuthSecondIdentityProvider provider;

        public EndpointCurrent(AuthenticationCallback callback,
                               RealmModel realm,
                               EventBuilder event,
                               JustAuthSecondIdentityProvider provider) {
            super(callback, realm, event, provider);
            this.provider = provider;
        }

        @GET
        public Response authResponse(@QueryParam(AbstractOAuth2IdentityProvider.OAUTH2_PARAMETER_STATE) String state,
                                     @QueryParam(AbstractOAuth2IdentityProvider.OAUTH2_PARAMETER_CODE) String authorizationCode,
                                     @QueryParam(OAuth2Constants.ERROR) String error,
                                     @QueryParam(OAuth2Constants.ERROR_DESCRIPTION) String errorDescription) {
            OAuth2IdentityProviderConfig providerConfig = provider.getConfig();

            if (state == null) {
                logErroneousRedirectUrlError("Redirection URL does not contain a state parameter", providerConfig);
                return errorIdentityProviderLogin(Messages.IDENTITY_PROVIDER_MISSING_STATE_ERROR);
            }

            try {
                AuthenticationSessionModel authSession = this.callback.getAndVerifyAuthenticationSession(state);
                session.getContext().setAuthenticationSession(authSession);

                if (error != null) {
                    logErroneousRedirectUrlError("Redirection URL contains an error", providerConfig);
                    if (error.equals(ACCESS_DENIED)) {
                        return callback.cancelled(providerConfig);
                    } else if (error.equals(OAuthErrorException.LOGIN_REQUIRED) || error.equals(OAuthErrorException.INTERACTION_REQUIRED)) {
                        return callback.error(error);
                    } else if (error.equals(OAuthErrorException.TEMPORARILY_UNAVAILABLE) && Constants.AUTHENTICATION_EXPIRED_MESSAGE.equals(errorDescription)) {
                        return callback.retryLogin(this.provider, authSession);
                    } else {
                        return callback.error(Messages.IDENTITY_PROVIDER_UNEXPECTED_ERROR);
                    }
                }

                if (authorizationCode == null) {
                    logErroneousRedirectUrlError("Redirection URL neither contains a code nor error parameter",
                            providerConfig);
                    return errorIdentityProviderLogin(Messages.IDENTITY_PROVIDER_MISSING_CODE_OR_ERROR_ERROR);
                }

                logger.infof("authResponse: authorizationCode=%s state=%s", authorizationCode, state);
                AuthCallback authCallback = AuthCallback.builder()
                        .code(authorizationCode)
                        .state(state)
                        .build();

                AuthRequest authRequest = getAuthRequest(AUTH_CONFIG, AUTH_CONFIG.getRedirectUri());
                logger.infof("auth config, id: %s, secret: %s, redirect: %s",
                        AUTH_CONFIG.getClientId(), AUTH_CONFIG.getClientSecret(), AUTH_CONFIG.getRedirectUri());
                AuthResponse<AuthUser> response = authRequest.login(authCallback);

                logger.infof("authResponse: response=%s", response.getMsg());
                if (!response.ok()) {
                    logger.errorf("Unexpected response from token endpoint %s. status=%s, response=%s",
                            "null", response.getCode(), response);
                    return errorIdentityProviderLogin(Messages.IDENTITY_PROVIDER_UNEXPECTED_ERROR);
                }

                AuthUser authUser = response.getData();
                JustAuthIdentityProviderConfig config = JustAuthSecondIdentityProvider.this.getConfig();
                BrokeredIdentityContext federatedIdentity = new BrokeredIdentityContext(authUser.getUuid(), config);
                authUser.getRawUserInfo().forEach((k, v) -> {
                    String value = (v instanceof String) ? v.toString() : JSONUtil.toJsonStr(v);
                    // v  不能过长
                    federatedIdentity.setUserAttribute(config.getAlias() + "-" + k, value);
                });

                if (providerConfig.isStoreToken()) {
                    // make sure that token wasn't already set by getFederatedIdentity();
                    // want to be able to allow provider to set the token itself.
                    if (federatedIdentity.getToken() == null) {
                        federatedIdentity.setToken(authUser.getToken().getAccessToken());
                    }
                }

                federatedIdentity.setUsername(authUser.getUuid());
                federatedIdentity.setEmail(authUser.getEmail());
                federatedIdentity.setFirstName(authUser.getNickname());
                federatedIdentity.setLastName("");
                federatedIdentity.setBrokerUserId(authUser.getUuid());

                federatedIdentity.setIdp(provider);
                federatedIdentity.setAuthenticationSession(authSession);
                return callback.authenticated(federatedIdentity);
            } catch (WebApplicationException e) {
                return e.getResponse();
            } catch (IdentityBrokerException e) {
                if (e.getMessageCode() != null) {
                    return errorIdentityProviderLogin(e.getMessageCode());
                }
                logger.error("Failed to make identity provider oauth callback", e);
                return errorIdentityProviderLogin(Messages.IDENTITY_PROVIDER_UNEXPECTED_ERROR);
            } catch (Exception e) {
                logger.error("Failed to make identity provider oauth callback", e);
                return errorIdentityProviderLogin(Messages.IDENTITY_PROVIDER_UNEXPECTED_ERROR);
            }
        }

        private void logErroneousRedirectUrlError(String mainMessage, OAuth2IdentityProviderConfig providerConfig) {
            String providerId = providerConfig.getProviderId();
            String redirectionUrl = session.getContext().getUri().getRequestUri().toString();

            logger.errorf("%s. providerId=%s, redirectionUrl=%s", mainMessage, providerId, redirectionUrl);
        }

        private Response errorIdentityProviderLogin(String message) {
            event.event(EventType.IDENTITY_PROVIDER_LOGIN);
            event.error(Errors.IDENTITY_PROVIDER_LOGIN_FAILURE);
            return ErrorPage.error(session, null, Response.Status.BAD_GATEWAY, message);
        }

    }

    @Override
    protected String getDefaultScopes() {
        return DEFAULT_SCOPES;
    }

}

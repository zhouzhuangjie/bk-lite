package org.neverland.social;

import me.zhyd.oauth.request.AuthWeChatOpenRequest;
import org.keycloak.broker.oidc.OAuth2IdentityProviderConfig;
import org.keycloak.broker.provider.AbstractIdentityProviderFactory;
import org.keycloak.broker.social.SocialIdentityProviderFactory;
import org.keycloak.models.IdentityProviderModel;
import org.keycloak.models.KeycloakSession;
import org.keycloak.provider.ProviderConfigProperty;
import org.keycloak.provider.ProviderConfigurationBuilder;
import org.neverland.social.common.JustAuthIdentityProviderConfig;
import org.neverland.social.common.JustAuthKey;
import org.neverland.social.common.JustAuthSecondIdentityProvider;

import java.util.List;

public class WechatMpIdentityProviderFactory extends
        AbstractIdentityProviderFactory<JustAuthSecondIdentityProvider>
        implements SocialIdentityProviderFactory<JustAuthSecondIdentityProvider> {

    public static final JustAuthKey JUST_AUTH_KEY = JustAuthKey.WE_CHAT_MP;

    @Override
    public String getName() {
        return JUST_AUTH_KEY.getName();
    }

    @Override
    public JustAuthSecondIdentityProvider create(KeycloakSession session, IdentityProviderModel model) {
        return new JustAuthSecondIdentityProvider(session,
                new JustAuthIdentityProviderConfig(model, JUST_AUTH_KEY, AuthWeChatOpenRequest::new));
    }

    @Override
    public OAuth2IdentityProviderConfig createConfig() {
        return new OAuth2IdentityProviderConfig();
    }

    @Override
    public String getId() {
        return JUST_AUTH_KEY.getId();
    }

    @Override
    public List<ProviderConfigProperty> getConfigProperties() {
        return ProviderConfigurationBuilder.create().property()
                .name("oauthCallbackUrl")
                .label("OAuth Callback Url")
                .helpText("OAuth callback url.")
                .type(ProviderConfigProperty.STRING_TYPE)
                .required(true)
                .add().build();
    }
}
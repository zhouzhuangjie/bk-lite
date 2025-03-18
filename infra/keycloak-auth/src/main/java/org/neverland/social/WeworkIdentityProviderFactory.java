package org.neverland.social;

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
import org.neverland.social.compatible.JustAuthWeChatEnterpriseQrcodeV2Request;
import java.util.List;


public class WeworkIdentityProviderFactory extends
        AbstractIdentityProviderFactory<JustAuthSecondIdentityProvider>
        implements SocialIdentityProviderFactory<JustAuthSecondIdentityProvider> {

    public static final JustAuthKey JUST_AUTH_KEY = JustAuthKey.WEWORK;

    @Override
    public String getName() {
        return JUST_AUTH_KEY.getName();
    }

    @Override
    public JustAuthSecondIdentityProvider create(KeycloakSession session, IdentityProviderModel model) {
        return new JustAuthSecondIdentityProvider(session,
                new JustAuthIdentityProviderConfig(model, JUST_AUTH_KEY, JustAuthWeChatEnterpriseQrcodeV2Request::new));
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
        return ProviderConfigurationBuilder.create()
                .property()
                .name("weworkAgentId")
                .label("Agent Id")
                .helpText("agent id.")
                .type(ProviderConfigProperty.STRING_TYPE)
                .required(true)
                .add()
                .property()
                .name("oauthCallbackUrl")
                .label("OAuth Callback Url")
                .helpText("OAuth callback url.")
                .type(ProviderConfigProperty.STRING_TYPE)
                .required(true)
                .add()
                .build();
    }

}

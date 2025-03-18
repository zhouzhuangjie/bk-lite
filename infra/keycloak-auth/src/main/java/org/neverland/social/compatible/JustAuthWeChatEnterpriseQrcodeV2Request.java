package org.neverland.social.compatible;

import com.alibaba.fastjson.JSONObject;
import me.zhyd.oauth.cache.AuthStateCache;
import me.zhyd.oauth.config.AuthConfig;
import me.zhyd.oauth.config.AuthDefaultSource;
import me.zhyd.oauth.enums.AuthResponseStatus;
import me.zhyd.oauth.enums.AuthUserGender;
import me.zhyd.oauth.exception.AuthException;
import me.zhyd.oauth.model.AuthToken;
import me.zhyd.oauth.model.AuthUser;
import me.zhyd.oauth.request.AbstractAuthWeChatEnterpriseRequest;
import me.zhyd.oauth.utils.GlobalAuthUtils;
import me.zhyd.oauth.utils.HttpUtils;
import me.zhyd.oauth.utils.StringUtils;
import me.zhyd.oauth.utils.UrlBuilder;
import org.jboss.logging.Logger;

/**
 * <p>
 * 新版企业微信 Web 登录，参考 <a href="https://developer.work.weixin.qq.com/document/path/98152">https://developer.work.weixin.qq.com/document/path/98152</a>
 * </p>
 *
 * @author yadong.zhang (yadong.zhang0415(a)gmail.com)
 * @since 1.16.7
 */
public class JustAuthWeChatEnterpriseQrcodeV2Request extends AbstractAuthWeChatEnterpriseRequest {
    protected static final Logger logger = Logger.getLogger(JustAuthWeChatEnterpriseQrcodeV2Request.class);

    public JustAuthWeChatEnterpriseQrcodeV2Request(AuthConfig config) {
        super(config, AuthDefaultSource.WECHAT_ENTERPRISE_V2);
    }

    public JustAuthWeChatEnterpriseQrcodeV2Request(AuthConfig config, AuthStateCache authStateCache) {
        super(config, AuthDefaultSource.WECHAT_ENTERPRISE_V2, authStateCache);
    }

    @Override
    public AuthUser getUserInfo(AuthToken authToken) {
        String response = doGetUserInfo(authToken);
        logger.infof("get user info: %s", response);
        JSONObject object = this.checkResponse(response);

        // 返回 OpenId 或其他，均代表非当前企业用户，不支持
        if (!object.containsKey("userid")) {
            throw new AuthException(AuthResponseStatus.UNIDENTIFIED_PLATFORM, source);
        }

        String userId = object.getString("userid");
        String userTicket = object.getString("user_ticket");
        JSONObject userDetail = getUserDetail(authToken.getAccessToken(), userId, userTicket);
        logger.infof("get user detail: %s", userDetail);
        return AuthUser.builder()
                .rawUserInfo(userDetail)
                .username(userDetail.getString("name"))
                .nickname(userDetail.getString("alias"))
                .avatar(userDetail.getString("avatar"))
                .location(userDetail.getString("address"))
                .email(userDetail.getString("email"))
                .uuid(userId)
                .gender(AuthUserGender.getWechatRealGender(userDetail.getString("gender")))
                .token(authToken)
                .source(source.toString())
                .build();
    }

    /**
     * 用户详情
     *
     * @param accessToken accessToken
     * @param userId      企业内用户id
     * @param userTicket  成员票据，用于获取用户信息或敏感信息
     * @return 用户详情
     */
    private JSONObject getUserDetail(String accessToken, String userId, String userTicket) {
        // 用户基础信息
        String userInfoUrl = UrlBuilder.fromBaseUrl("https://qyapi.weixin.qq.com/cgi-bin/user/get")
                .queryParam("access_token", accessToken)
                .queryParam("userid", userId)
                .build();
        String userInfoResponse = new HttpUtils(config.getHttpConfig()).get(userInfoUrl).getBody();
        JSONObject userInfo = checkResponse(userInfoResponse);

        // 用户敏感信息
        if (StringUtils.isNotEmpty(userTicket)) {
            String userDetailUrl = UrlBuilder.fromBaseUrl("https://qyapi.weixin.qq.com/cgi-bin/auth/getuserdetail")
                    .queryParam("access_token", accessToken)
                    .build();
            JSONObject param = new JSONObject();
            param.put("user_ticket", userTicket);
            String userDetailResponse = new HttpUtils(config.getHttpConfig()).post(userDetailUrl, param.toJSONString()).getBody();
            JSONObject userDetail = checkResponse(userDetailResponse);

            userInfo.putAll(userDetail);
        }
        return userInfo;
    }

    /**
     * 校验请求结果
     *
     * @param response 请求结果
     * @return 如果请求结果正常，则返回JSONObject
     */
    private JSONObject checkResponse(String response) {
        JSONObject object = JSONObject.parseObject(response);

        if (object.containsKey("errcode") && object.getIntValue("errcode") != 0) {
            throw new AuthException(object.getString("errmsg"), source);
        }

        return object;
    }

    @Override
    public String authorize(String state) {
        return UrlBuilder.fromBaseUrl(source.authorize())
                .queryParam("login_type", config.getLoginType())
                // 登录类型为企业自建应用/服务商代开发应用时填企业 CorpID，第三方登录时填登录授权 SuiteID
                .queryParam("appid", config.getClientId())
                // 企业自建应用/服务商代开发应用 AgentID，当login_type=CorpApp时填写
                .queryParam("agentid", config.getAgentId())
                .queryParam("redirect_uri", GlobalAuthUtils.urlEncode(config.getRedirectUri()))
                .queryParam("state", getRealState(state))
                .queryParam("lang", config.getLang())
                .build()
                .concat("#wechat_redirect");
    }

    @Override
    protected void checkConfig(AuthConfig config) {
        super.checkConfig(config);
        if ("CorpApp".equals(config.getLoginType()) && StringUtils.isEmpty(config.getAgentId())) {
            throw new AuthException(AuthResponseStatus.ILLEGAL_WECHAT_AGENT_ID, source);
        }
    }

}

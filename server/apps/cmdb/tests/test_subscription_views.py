from apps.cmdb.models.subscription_rule import SubscriptionRule

import pytest

pytestmark = pytest.mark.django_db
SUBSCRIPTION_URL = "/api/v1/cmdb/api/subscription/"


def authorize(user, permission):
    user.permission = {"cmdb": {permission}}


def rule_payload(organization):
    return {
        "name": f"scope-{organization}",
        "organization": organization,
        "model_id": "host",
        "filter_type": "instances",
        "instance_filter": {"instance_ids": [1]},
        "trigger_types": ["attribute_change"],
        "trigger_config": {"attribute_change": {"fields": ["cpu"]}},
        "recipients": {"users": ["alice"], "groups": []},
        "channel_ids": [1],
    }


def test_create_rejects_forged_current_team(mocker, api_client, authenticated_user):
    authorize(authenticated_user, "asset_info-Add")
    api_client.cookies["current_team"] = "9"
    mocker.patch(
        "apps.core.utils.current_team_scope.resolve_assignable_organization_ids",
        return_value=frozenset({1, 2}),
    )
    mocker.patch(
        "apps.cmdb.views.subscription.GroupUtils.get_group_with_descendants",
        return_value=[9],
    )
    response = api_client.post(SUBSCRIPTION_URL, rule_payload(9), format="json")

    assert response.status_code == 403
    assert SubscriptionRule.objects.count() == 0


def test_update_rejects_forged_current_team(mocker, api_client, authenticated_user):
    authorize(authenticated_user, "asset_info-Edit")
    api_client.cookies["current_team"] = "9"
    rule = SubscriptionRule.objects.create(**rule_payload(9))
    payload = rule_payload(2)
    payload["name"] = "forged-update"
    mocker.patch(
        "apps.core.utils.current_team_scope.resolve_assignable_organization_ids",
        return_value=frozenset({1, 2}),
    )
    mocker.patch(
        "apps.cmdb.views.subscription.GroupUtils.get_group_with_descendants",
        return_value=[9, 2],
    )
    response = api_client.put(
        f"{SUBSCRIPTION_URL}{rule.id}/", payload, format="json"
    )

    assert response.status_code == 403
    rule.refresh_from_db()
    assert rule.name == "scope-9"


def test_create_preserves_authorized_descendant_organization(
    mocker, api_client, authenticated_user
):
    authorize(authenticated_user, "asset_info-Add")
    api_client.cookies["current_team"] = "1"
    mocker.patch(
        "apps.core.utils.current_team_scope.resolve_assignable_organization_ids",
        return_value=frozenset({1, 2}),
    )
    mocker.patch(
        "apps.system_mgmt.utils.group_utils.GroupUtils.get_group_with_descendants",
        return_value=[1, 2],
    )
    response = api_client.post(SUBSCRIPTION_URL, rule_payload(2), format="json")

    assert response.status_code == 200
    assert SubscriptionRule.objects.get().organization == 2

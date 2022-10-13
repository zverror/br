from typing import cast

import pytest

from baserow.core.action.handler import ActionHandler
from baserow.core.action.registries import action_type_registry
from baserow_enterprise.models import Team, TeamSubject
from baserow_enterprise.scopes import TeamsActionScopeType
from baserow_enterprise.teams.actions import (
    CreateTeamActionType,
    CreateTeamSubjectActionType,
    DeleteTeamActionType,
    DeleteTeamSubjectActionType,
    UpdateTeamActionType,
)
from baserow_enterprise.teams.handler import TeamForUpdate


@pytest.fixture(autouse=True)
def enable_enterprise_for_all_tests_here(enable_enterprise):
    pass


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_creating_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    action_type_registry.get_by_type(CreateTeamActionType).do(user, "test", group)

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)

    assert Team.objects.filter(group=group).count() == 0


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_creating_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    team1 = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "test1", group
    )
    team2 = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "test2", group
    )

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)

    assert not Team.objects.filter(pk=team2.id).exists()
    assert Team.objects.filter(pk=team1.id).exists()

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)

    assert Team.objects.filter(pk=team2.id).exists()
    assert Team.objects.filter(pk=team1.id).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_updating_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    original_team = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "original name", group
    )

    updated_team = action_type_registry.get_by_type(UpdateTeamActionType).do(
        user, cast(TeamForUpdate, original_team), "updated name"
    )

    assert updated_team.name == "updated name"
    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    group.refresh_from_db()
    assert updated_team.name == original_team.name


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_updating_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    original_team = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "original name", group
    )

    updated_team = action_type_registry.get_by_type(UpdateTeamActionType).do(
        user, cast(TeamForUpdate, original_team), "updated name"
    )
    assert updated_team.name == "updated name"

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    group.refresh_from_db()
    assert updated_team.name == original_team.name

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)
    group.refresh_from_db()
    assert updated_team.name == updated_team.name


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_deleting_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    team = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "test", group
    )
    assert Team.objects.filter(pk=team.pk).exists()

    action_type_registry.get_by_type(DeleteTeamActionType).do(user, team)
    assert not Team.objects.filter(pk=team.pk).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert Team.objects.filter(pk=team.pk).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_deleting_team(data_fixture):
    session_id = "session-id"
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group(user=user)

    team = action_type_registry.get_by_type(CreateTeamActionType).do(
        user, "test", group
    )
    assert Team.objects.filter(pk=team.pk).exists()

    action_type_registry.get_by_type(DeleteTeamActionType).do(user, team)
    assert not Team.objects.filter(pk=team.pk).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert Team.objects.filter(pk=team.pk).exists()

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert not Team.objects.filter(pk=team.pk).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_creating_subject_by_id(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"id": invitee.id}, "auth_user", team
    )

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)

    assert not TeamSubject.objects.filter(team=team).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_creating_subject_by_id(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    subject = action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"id": invitee.id}, "auth_user", team
    )
    assert TeamSubject.objects.filter(pk=subject.id).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert not TeamSubject.objects.filter(pk=subject.id).exists()

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert TeamSubject.objects.filter(pk=subject.id).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_creating_subject_by_email(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"email": invitee.email}, "auth_user", team
    )

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)

    assert not TeamSubject.objects.filter(team=team).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_creating_subject_by_email(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    subject = action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"email": invitee.email}, "auth_user", team
    )
    assert TeamSubject.objects.filter(pk=subject.id).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert not TeamSubject.objects.filter(pk=subject.id).exists()

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert TeamSubject.objects.filter(pk=subject.id).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_deleting_team_subject(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    subject = action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"id": invitee.id}, "auth_user", team
    )
    subject_id = subject.id
    assert TeamSubject.objects.filter(pk=subject_id).exists()

    action_type_registry.get_by_type(DeleteTeamSubjectActionType).do(user, subject)
    assert not TeamSubject.objects.filter(pk=subject_id).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert TeamSubject.objects.filter(pk=subject_id).exists()


@pytest.mark.django_db
@pytest.mark.undo_redo
def test_can_undo_redo_deleting_team_subject(data_fixture, enterprise_data_fixture):
    session_id = "session-id"
    invitee = data_fixture.create_user()
    user = data_fixture.create_user(session_id=session_id)
    group = data_fixture.create_group()
    team = enterprise_data_fixture.create_team(group=group)

    subject = action_type_registry.get_by_type(CreateTeamSubjectActionType).do(
        user, {"id": invitee.id}, "auth_user", team
    )
    subject_id = subject.id
    assert TeamSubject.objects.filter(pk=subject_id).exists()

    action_type_registry.get_by_type(DeleteTeamSubjectActionType).do(user, subject)
    assert not TeamSubject.objects.filter(pk=subject_id).exists()

    ActionHandler.undo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert TeamSubject.objects.filter(pk=subject_id).exists()

    ActionHandler.redo(user, [TeamsActionScopeType.value(group.id)], session_id)
    assert not TeamSubject.objects.filter(pk=subject_id).exists()

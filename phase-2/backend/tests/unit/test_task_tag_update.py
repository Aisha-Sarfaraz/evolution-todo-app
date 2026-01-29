"""Task tag update unit tests.

T109: [US5] Unit test for tag assignment in task update

Tests:
- TaskUpdate accepts tag_ids list
- TaskUpdate accepts empty tag_ids (clears tags)
- TaskUpdate accepts None tag_ids (no change)
- Tag IDs must be valid UUIDs

@see specs/001-fullstack-todo-web/spec.md - FR-065, FR-066
"""

import pytest
from uuid import uuid4
from pydantic import ValidationError

from src.models.task import TaskUpdate


class TestTaskUpdateTagIds:
    """Test tag_ids validation in TaskUpdate schema."""

    def test_tag_ids_accepts_list_of_uuids(self):
        """TaskUpdate accepts a list of valid UUIDs for tag_ids."""
        tag_id_1 = uuid4()
        tag_id_2 = uuid4()

        update = TaskUpdate(tag_ids=[tag_id_1, tag_id_2])

        assert update.tag_ids == [tag_id_1, tag_id_2]
        assert len(update.tag_ids) == 2

    def test_tag_ids_accepts_empty_list(self):
        """TaskUpdate accepts empty list for tag_ids (clears all tags)."""
        update = TaskUpdate(tag_ids=[])

        assert update.tag_ids == []
        assert len(update.tag_ids) == 0

    def test_tag_ids_defaults_to_none(self):
        """TaskUpdate defaults tag_ids to None when not provided."""
        update = TaskUpdate(title="Test")

        assert update.tag_ids is None

    def test_tag_ids_accepts_none(self):
        """TaskUpdate accepts explicit None for tag_ids."""
        update = TaskUpdate(tag_ids=None)

        assert update.tag_ids is None

    def test_tag_ids_with_single_uuid(self):
        """TaskUpdate accepts single UUID in tag_ids list."""
        tag_id = uuid4()

        update = TaskUpdate(tag_ids=[tag_id])

        assert update.tag_ids == [tag_id]
        assert len(update.tag_ids) == 1

    def test_tag_ids_preserves_order(self):
        """TaskUpdate preserves order of tag_ids."""
        tag_ids = [uuid4() for _ in range(5)]

        update = TaskUpdate(tag_ids=tag_ids)

        assert update.tag_ids == tag_ids

    def test_tag_ids_with_string_uuid(self):
        """TaskUpdate accepts string UUIDs that can be converted."""
        tag_id_str = str(uuid4())

        update = TaskUpdate(tag_ids=[tag_id_str])

        assert len(update.tag_ids) == 1

    def test_tag_ids_rejects_invalid_uuid(self):
        """TaskUpdate rejects invalid UUID strings."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(tag_ids=["not-a-uuid"])

        assert "tag_ids" in str(exc_info.value).lower()

    def test_tag_ids_rejects_integer(self):
        """TaskUpdate rejects integer for tag_ids."""
        with pytest.raises(ValidationError):
            TaskUpdate(tag_ids=123)

    def test_tag_ids_rejects_string(self):
        """TaskUpdate rejects plain string for tag_ids."""
        with pytest.raises(ValidationError):
            TaskUpdate(tag_ids="some-string")


class TestTaskUpdatePartialWithTags:
    """Test partial updates with tag_ids."""

    def test_partial_update_with_title_and_tags(self):
        """TaskUpdate accepts title and tag_ids together."""
        tag_id = uuid4()

        update = TaskUpdate(title="New Title", tag_ids=[tag_id])

        assert update.title == "New Title"
        assert update.tag_ids == [tag_id]
        assert update.description is None
        assert update.priority is None

    def test_partial_update_tags_only(self):
        """TaskUpdate accepts only tag_ids (partial update)."""
        tag_ids = [uuid4(), uuid4()]

        update = TaskUpdate(tag_ids=tag_ids)

        assert update.tag_ids == tag_ids
        assert update.title is None
        assert update.description is None
        assert update.priority is None
        assert update.category_id is None

    def test_model_dump_excludes_unset_tag_ids(self):
        """model_dump(exclude_unset=True) excludes tag_ids when not provided."""
        update = TaskUpdate(title="Test")

        dumped = update.model_dump(exclude_unset=True)

        assert "title" in dumped
        assert "tag_ids" not in dumped

    def test_model_dump_includes_set_tag_ids(self):
        """model_dump(exclude_unset=True) includes tag_ids when provided."""
        tag_id = uuid4()
        update = TaskUpdate(tag_ids=[tag_id])

        dumped = update.model_dump(exclude_unset=True)

        assert "tag_ids" in dumped
        assert dumped["tag_ids"] == [tag_id]

    def test_model_dump_includes_empty_tag_ids(self):
        """model_dump(exclude_unset=True) includes empty tag_ids when explicitly set."""
        update = TaskUpdate(tag_ids=[])

        dumped = update.model_dump(exclude_unset=True)

        assert "tag_ids" in dumped
        assert dumped["tag_ids"] == []

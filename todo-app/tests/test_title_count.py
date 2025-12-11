"""Tests for page title with incomplete todo count feature."""

import pytest
from app.database import Todo


class TestTitleCount:
    """Tests for page title with incomplete todo count."""

    def test_app_page_includes_incomplete_count_in_context(
        self, authenticated_client, test_list, db_session
    ):
        """Test that app page includes incomplete_count in template context."""
        # Add some todos
        todo1 = Todo(list_id=test_list.id, title="Incomplete 1", position=0, is_completed=False)
        todo2 = Todo(list_id=test_list.id, title="Completed", position=1, is_completed=True)
        todo3 = Todo(list_id=test_list.id, title="Incomplete 2", position=2, is_completed=False)
        db_session.add_all([todo1, todo2, todo3])
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200

        # Check that the title shows the count
        content = response.content.decode()
        assert f"<title>(2) {test_list.name} - Todo App</title>" in content

    def test_app_page_no_count_when_all_complete(
        self, authenticated_client, test_list, db_session
    ):
        """Test that title has no count when all todos are complete."""
        # Add completed todos
        todo1 = Todo(list_id=test_list.id, title="Completed 1", position=0, is_completed=True)
        todo2 = Todo(list_id=test_list.id, title="Completed 2", position=1, is_completed=True)
        db_session.add_all([todo1, todo2])
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200

        # Check that the title has no count
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content
        assert "(0)" not in content  # Should not show (0)

    def test_app_page_no_count_when_list_empty(
        self, authenticated_client, test_list, db_session
    ):
        """Test that title has no count when list is empty."""
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        assert response.status_code == 200

        # Check that the title has no count
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content

    def test_toggle_todo_returns_title_update_oob(
        self, authenticated_client, test_list, test_todo, db_session
    ):
        """Test that toggling a todo returns OOB update for title."""
        # Ensure todo is incomplete initially
        test_todo.is_completed = False
        db_session.commit()

        response = authenticated_client.patch(f"/api/todos/{test_todo.id}/toggle")
        assert response.status_code == 200

        # Check response includes title OOB update
        content = response.content.decode()
        assert 'id="page-title-data"' in content
        assert 'hx-swap-oob="true"' in content

    def test_create_todo_returns_title_update_oob(
        self, authenticated_client, test_list, db_session
    ):
        """Test that creating a todo returns OOB update for title."""
        response = authenticated_client.post(
            "/api/todos",
            data={
                "list_id": test_list.id,
                "title": "New Todo",
            },
        )
        assert response.status_code == 200

        # Check response includes title OOB update
        content = response.content.decode()
        assert 'id="page-title-data"' in content
        assert 'hx-swap-oob="true"' in content

    def test_delete_todo_returns_title_update_oob(
        self, authenticated_client, test_todo, db_session
    ):
        """Test that deleting a todo returns OOB update for title."""
        response = authenticated_client.delete(f"/api/todos/{test_todo.id}")
        assert response.status_code == 200

        # Check response includes title OOB update
        content = response.content.decode()
        assert 'id="page-title-data"' in content
        assert 'hx-swap-oob="true"' in content

    def test_title_count_updates_dynamically(
        self, authenticated_client, test_list, db_session
    ):
        """Test that title count updates as todos are added/completed."""
        # Start with empty list
        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content

        # Add an incomplete todo
        todo1 = Todo(list_id=test_list.id, title="Todo 1", position=0, is_completed=False)
        db_session.add(todo1)
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        content = response.content.decode()
        assert f"<title>(1) {test_list.name} - Todo App</title>" in content

        # Add another incomplete todo
        todo2 = Todo(list_id=test_list.id, title="Todo 2", position=1, is_completed=False)
        db_session.add(todo2)
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        content = response.content.decode()
        assert f"<title>(2) {test_list.name} - Todo App</title>" in content

        # Complete one todo
        todo1.is_completed = True
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        content = response.content.decode()
        assert f"<title>(1) {test_list.name} - Todo App</title>" in content

        # Complete the other todo
        todo2.is_completed = True
        db_session.commit()

        response = authenticated_client.get(f"/app/lists/{test_list.id}")
        content = response.content.decode()
        assert f"<title>{test_list.name} - Todo App</title>" in content

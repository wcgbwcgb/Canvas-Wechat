"""Tests for notification plain-text formatting."""


def test_format_overdue_alert():
    from app.notifications.formatter import format_overdue_alert

    result = format_overdue_alert(
        course_name="生物101",
        assignment_name="实验报告3",
        due_at_str="2026-06-20 23:59",
        days_overdue=2,
        html_url="https://canvas.univ.edu/courses/1/assignments/2",
    )

    assert "⚠️ 作业逾期提醒" in result
    assert "生物101" in result
    assert "实验报告3" in result
    assert "2026-06-20 23:59" in result
    assert "已逾期 2 天" in result
    assert "https://canvas.univ.edu" in result


def test_format_due_soon_alert():
    from app.notifications.formatter import format_due_soon_alert

    result = format_due_soon_alert(
        course_name="数学202",
        assignment_name="习题集6",
        due_at_str="2026-06-22 17:00",
        hours_left=4.5,
        html_url="https://canvas.univ.edu/courses/3/assignments/4",
    )

    assert "🔴 作业即将截止" in result
    assert "数学202" in result
    assert "习题集6" in result
    assert "4 小时" in result


def test_format_new_announcement():
    from app.notifications.formatter import format_new_announcement

    result = format_new_announcement(
        course_name="CS 101",
        title="期中考试日期变更",
        html_url="https://canvas.univ.edu/courses/5/announcements/10",
    )

    assert "📢 新公告" in result
    assert "CS 101" in result
    assert "期中考试日期变更" in result


def test_format_bind_success():
    from app.notifications.formatter import format_bind_success

    result = format_bind_success("张三", 3)

    assert "✅ 绑定成功" in result
    assert "张三" in result
    assert "3 门课程" in result

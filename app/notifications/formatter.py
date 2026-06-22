"""Plain-text notification formatting using Emoji + separators.

No template messages available on iLink Bot API — pure text only.
"""


def format_overdue_alert(
    course_name: str,
    assignment_name: str,
    due_at_str: str,
    days_overdue: int,
    html_url: str,
) -> str:
    return (
        "⚠️ 作业逾期提醒\n"
        "\n"
        f"📚 {course_name}\n"
        f"📝 {assignment_name}\n"
        f"📅 截止：{due_at_str}\n"
        f"⏰ 已逾期 {days_overdue} 天\n"
        "\n"
        f"🔗 {html_url}"
    )


def format_due_soon_alert(
    course_name: str,
    assignment_name: str,
    due_at_str: str,
    hours_left: float,
    html_url: str,
) -> str:
    urgency = "🔴" if hours_left <= 6 else "🟡"
    return (
        f"{urgency} 作业即将截止\n"
        "\n"
        f"📚 {course_name}\n"
        f"📝 {assignment_name}\n"
        f"📅 截止：{due_at_str}\n"
        f"⏰ 剩余 {hours_left:.0f} 小时\n"
        "\n"
        f"🔗 {html_url}"
    )


def format_new_announcement(
    course_name: str,
    title: str,
    html_url: str,
) -> str:
    return (
        "📢 新公告\n"
        "\n"
        f"📚 {course_name}\n"
        f"📌 {title}\n"
        "\n"
        f"🔗 {html_url}"
    )


def format_grade_posted(
    course_name: str,
    assignment_name: str,
    score: float | None,
    html_url: str,
) -> str:
    score_str = f"{score} 分" if score is not None else "已评分"
    return (
        "📊 成绩已发布\n"
        "\n"
        f"📚 {course_name}\n"
        f"📝 {assignment_name}\n"
        f"🏆 {score_str}\n"
        "\n"
        f"🔗 {html_url}"
    )


def format_bind_success(
    canvas_name: str,
    course_count: int,
) -> str:
    return (
        f"✅ 绑定成功！欢迎你，{canvas_name}！\n"
        "\n"
        f"📚 已同步 {course_count} 门课程\n"
        "\n"
        "你可以问我：\n"
        "  • 这周有什么作业？\n"
        "  • 我的成绩怎么样？\n"
        "  • 最近有什么新公告？"
    )

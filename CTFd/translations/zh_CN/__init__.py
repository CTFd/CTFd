# todo: split into modules and merge the dicts

api_v1 = {
    "awards.user.not_team_member": "用户没有加入任何队伍，不可获得奖励",
    "challenges.type.not_installed": lambda type: "没有安装提供题目类型<{}>的插件，无法加载题目。".format(type),
    "challenges.attempt.game_paused": lambda name: "{}已暂停".format(name),
    "challenges.attempt.ratelimited": "提交频率过高，请稍后再试。",
    "challenges.attempt.attempts_left": lambda attempts: "还剩{}次机会".format(attempts),
    "challenges.attempt.already_solved": "你已经解出该题目",
    "hints.view.unmet_prerequisites": "前置提示未解锁，无法解锁该提示",
    "teams.edit.not_captain": "只有队长可以编辑队伍信息",
    "teams.delete.disabled": "队伍解散功能已被禁用",
    "teams.delete.not_captain": "只有队长可以解散队伍",
    "teams.delete.participated": (
        "当前队伍无法解散，因为这支队伍已经参加了比赛。"
        "如果仍需解散队伍或移除队员，请联系管理员。"
    ),
    "teams.member.invite.not_captain": "只有队长可以生成邀请码",
    "teams.member.join.conflict": "用户已经加入了一个队伍",
    "teams.member.delete.not_member": "此用户不在队伍中",
    "unlocks.insufficient_points": "积分不足，无法解锁该对象",
    "unlocks.already_unlocked": "你已解锁该对象",
    "users.edit.no_self_ban": "你不能禁用自己的账户",
    "users.delete.no_self_delete": "你不能删除自己的账户",
    "users.email.not_configured": "管理员未配置邮件发送参数",
    "users.email.text_empty": "邮件正文不能为空",
}

translations = {
    "challenges.name": "题目名称",
    "challenges.id": "题目ID",
    "challenges.category": "题目分类",
    "challenges.type": "题型",
    "constants.config.invalid_theme_settings": "主题设置无效",
    "forms.parameter": "参数",
    "forms.search": "搜索",
    "forms.submit": "提交",
    "forms.upload": "上传",
    "forms.auth.username": "用户名",
    "forms.auth.username_or_email": "用户名或邮箱",
    "forms.auth.email": "邮箱",
    "forms.auth.password": "密码",
    "forms.auth.resend_confirm_email": "重新发送确认邮件",
    "forms.challenge_files.files": "文件",
    "forms.challenge_files.files.desc": "使用Ctrl+单击或Command+单击来选择多个文件",
}
translations.update({
    "api.v1." + k: v
    for k, v in api_v1.items()
})

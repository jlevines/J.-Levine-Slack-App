from src.models.slack import Action, Attachment, Message


def message(name):

    attachment = Attachment(
        title="Opportunity Rejected",
        text="You have passed on this opportunity",
        callback_id="rej_opp_attachment",
        fallback="Opportunity Rejected",
        color="#ffcc00"
    )
    attachment.new_field(title="Opportunity Name", value=name)

    return Message(
        attachments=[attachment.built_message]
    ).built_message

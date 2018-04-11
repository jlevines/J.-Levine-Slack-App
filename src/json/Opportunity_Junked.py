from src.models.slack import Action, Attachment, Message


def message(name):

    attachment = Attachment(
        title="Opportunity Trashed",
        callback_id="junk_opp_attachment",
        fallback="Opportunity Trashed",
        color="#ef0404"
    )

    attachment.new_field(title="Opportunity Name", value=name)

    return Message(
        attachments=[attachment.built_message]
    ).built_message


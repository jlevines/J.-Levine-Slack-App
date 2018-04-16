from src.models.slack import Attachment, Message


def message(name):

    attachment = Attachment(
        title="Opportunity Expired",
        text="This opportunity has been reassigned. You have 15 minutes to accept a new opportunity.",
        callback_id="exp_opp_attachment",
        fallback="Opportunity Expired",
        color="#aaa5a5"
    )

    attachment.new_field(title="Opportunity Name", value=name)

    return attachment.built_message

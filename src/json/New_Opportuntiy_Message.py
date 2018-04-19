from src.models.slack import Action, Attachment, Message


def message(name, id, email="", phone="", main=""):
    actions = [
        Action(
            name="accept_opportunity",
            text="Accept Opportunity",
            type="button",
            style="primary",
            value=str({"status": "accepted", "lead_id": id})
        ),
        Action(
            name="reject_opportunity",
            text="Reject Opportunity",
            type="button",
            style="default",
            value=str({"status": "rejected", "lead_id": id})
        )]

    built_actions = [
        actions[0].built_message,
        actions[1].built_message
    ]

    attachment = Attachment(
        title="New Opportunity",
        text="A new opportunity has been made available to you.",
        callback_id="new_opp_attachment",
        fallback="Opportunity Url: {}".format("https://crm.zoho.com/crm/EntityInfo.do?module=Leads&id={}".format(id)),
        color="#3de5ff",
        actions=built_actions
    )

    attachment.new_field(
        title="Opportunity Name",
        value=name
    )

    attachment.new_field(
        title="Phone",
        value=phone,
        short=True
    )

    attachment.new_field(
        title="Email",
        value=email,
        short=True
    )

    attachment.new_field(
        title="Main Inquiry",
        value=main
    )

    return Message(
        attachments=[attachment.built_message]
    )

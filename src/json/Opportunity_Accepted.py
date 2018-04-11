from src.models.slack import Action, Attachment, Message


def message(name, phone, email, main, id):

    actions = [Action(
        name="new_opp_button",
        text="View Opportunity in Zoho",
        type="button",
        url="https://crm.zoho.com/crm/EntityInfo.do?module=Leads&id={}".format(id)
    ).built_message]

    attachment = Attachment(
        title="Opportunity Accepted",
        callback_id="new_opp_attachment",
        fallback="Opportunity Url: {}".format("https://crm.zoho.com/crm/EntityInfo.do?module=Leads&id={}".format(id)),
        color="#19c165",
        actions=actions
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
    ).built_message

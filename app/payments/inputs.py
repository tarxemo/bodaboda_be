import graphene

class DailySubmissionInput(graphene.InputObjectType):
    amount_tzs = graphene.Decimal(required=True)
    submission_date = graphene.Date(required=True)
    reference_number = graphene.String()
    comment = graphene.String()

class ApproveSubmissionInput(graphene.InputObjectType):
    submission_id = graphene.Int(required=True)
    status = graphene.String(required=True) # approved or rejected
    comment = graphene.String()

class ExpenseInput(graphene.InputObjectType):
    category = graphene.String(required=True)
    amount_tzs = graphene.Decimal(required=True)
    description = graphene.String(required=True)
    expense_date = graphene.Date(required=True)
    vehicle_id = graphene.Int()

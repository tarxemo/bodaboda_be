import graphene
from django.utils import timezone
from .models import Wallet, DailySubmission, Transaction
from .inputs import DailySubmissionInput, ApproveSubmissionInput, ExpenseInput
from .outputs import DailySubmissionType, FleetExpenseType
from fleet.models import RiderContract

class SubmitDailyFee(graphene.Mutation):
    class Arguments:
        input = DailySubmissionInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    submission = graphene.Field(DailySubmissionType)

    def mutate(self, info, input):
        rider = info.context.user
        if not rider.is_authenticated or rider.role != 'rider':
            return SubmitDailyFee(success=False, message="Only riders can submit fees.")

        # Find active contract to get owner and expected amount
        contract = RiderContract.objects.filter(rider=rider, is_active=True).first()
        if not contract:
            return SubmitDailyFee(success=False, message="No active contract found for this rider.")

        try:
            # Check if submission for this date already exists
            if DailySubmission.objects.filter(rider=rider, submission_date=input.submission_date).exists():
                return SubmitDailyFee(success=False, message=f"You already submitted a report for {input.submission_date}.")

            submission = DailySubmission.objects.create(
                rider=rider,
                owner=contract.owner,
                amount_tzs=input.amount_tzs,
                expected_amount_tzs=contract.daily_rent_tzs,
                submission_date=input.submission_date,
                reference_number=input.reference_number,
                comment=input.comment,
                status='pending'
            )
            return SubmitDailyFee(success=True, message="Submission recorded. Waiting for owner approval.", submission=submission)
        except Exception as e:
            return SubmitDailyFee(success=False, message=str(e))

class ProcessSubmission(graphene.Mutation):
    class Arguments:
        input = ApproveSubmissionInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        owner = info.context.user
        if not owner.is_authenticated or owner.role != 'owner':
            return ProcessSubmission(success=False, message="Not authorized.")

        try:
            submission = DailySubmission.objects.get(pk=input.submission_id, owner=owner)
            if submission.status != 'pending':
                return ProcessSubmission(success=False, message="This submission has already been processed.")

            if input.status == 'approved':
                submission.status = 'approved'
                submission.approved_at = timezone.now()
                submission.comment = input.comment
                submission.save()

                # Update Rider's Wallet Debt
                wallet, _ = Wallet.objects.get_or_create(user=submission.rider)
                wallet.total_debt_tzs -= submission.amount_tzs
                wallet.save()

                return ProcessSubmission(success=True, message="Submission approved and debt updated.")
            else:
                submission.status = 'rejected'
                submission.comment = input.comment
                submission.save()
                return ProcessSubmission(success=True, message="Submission rejected.")

        except DailySubmission.DoesNotExist:
            return ProcessSubmission(success=False, message="Submission not found.")


class RecordExpense(graphene.Mutation):
    class Arguments:
        input = ExpenseInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    expense = graphene.Field(FleetExpenseType)

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return RecordExpense(success=False, message="Not authorized.")

        try:
            from fleet.models import Vehicle
            vehicle = None
            if input.vehicle_id:
                # If owner, check they own it. If rider, check they are assigned to it?
                # For now, just allow if vehicle exists
                vehicle = Vehicle.objects.get(pk=input.vehicle_id)

            expense = FleetExpense.objects.create(
                user=user,
                vehicle=vehicle,
                category=input.category,
                amount_tzs=input.amount_tzs,
                description=input.description,
                expense_date=input.expense_date
            )
            return RecordExpense(success=True, message="Expense recorded successfully.", expense=expense)
        except Exception as e:
            return RecordExpense(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    submit_daily_fee = SubmitDailyFee.Field()
    process_submission = ProcessSubmission.Field()
    record_expense = RecordExpense.Field()

from rest_framework.routers import SimpleRouter

from avia_transportation.views import ContractViewSet

router = SimpleRouter()

router.register(r"contract", ContractViewSet, basename="contract")

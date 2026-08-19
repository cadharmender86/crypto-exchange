import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


async def test_admin_kyc_route_is_registered(client):
    response = await client.get("/api/v1/admin/kyc?page=1&page_size=1")

    assert response.status_code != 404, response.text
    assert response.status_code in {401, 403}, response.text

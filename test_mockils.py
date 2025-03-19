import xml.etree.ElementTree as ET
from fastapi.testclient import TestClient
from mockils import app
from aras_py.datastructures import xml_to_list

app.data_path = "test_data"
client = TestClient(app)

ns = {"mets": "http://www.loc.gov/METS/", "xlink": "http://www.w3.org/1999/xlink"}


def test_repository_root():
    response = client.get("/")
    assert response.status_code == 200


def test_repository_access_repositories():
    response = client.get("/access/repositories")
    assert response.status_code == 200
    repo_list = xml_to_list(response.content)
    assert repo_list[0] == "warc"


def test_repository_access_repositories_artifacts():
    response = client.get("/access/repositories/warc/artifacts")
    assert response.status_code == 200
    artifacts_list = xml_to_list(response.content)
    assert artifacts_list[0] == "1234"
    assert artifacts_list[1] == "12345"


def test_repository_access_repositories_single_artifact():
    response = client.get("/access/repositories/warc/artifacts/1234")
    assert response.status_code == 200
    # Not yet implemented


def test_repository_access_repositories_artifacts_objects():
    response = client.get("/access/repositories/warc/artifacts/1234/objects")
    assert response.status_code == 200
    tree = ET.fromstring(response.content)
    files = tree.findall("./mets:fileSec/mets:fileGrp/mets:file", ns)
    file = files[0]
    assert file.attrib["ID"] == "0"
    assert file.attrib["SIZE"] == "6"
    file_name = file.find("./mets:FLocat[@LOCTYPE='URL']", ns).get(
        f"{{{ns["xlink"]}}}href"
    )
    assert file_name == "bla.txt"


def test_repository_access_repositories_artifacts_single_object():
    response = client.get("/access/repositories/warc/artifacts/1234/objects/0")
    assert response.status_code == 200
    assert response.content.decode("utf-8") == "Hallo\n"

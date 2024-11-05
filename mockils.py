from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from textwrap import dedent
from pathlib import Path
import mimetypes
from datetime import datetime
import importlib
import mistune


def to_xml_list(items: list) -> str:
    return dedent(f"""
    <?xml version='1.0' encoding='UTF-8'?>
    <list>
        {"\n".join([f"<value>{entry.name}</value>" for entry in items])}
    </list>
    """)


def dir_to_mets_xml(files: list) -> str:
    mets_file_tpl = """
        <file ID="{id}" MIMETYPE="{mime_type}" CREATED="{now}" SIZE="{size}">
            <FLocat LOCTYPE="URL" xlink:href="{href}"/>
        </file>
        """

    mock_files = [
        mets_file_tpl.format(
            id=id,
            mime_type=mimetypes.guess_type(file),
            size=file.stat().st_size,
            href=file.name,
            now=datetime.now().isoformat(),
        )
        for id, file in enumerate(files)
    ]

    return dedent(f"""
        <?xml version='1.0' encoding='UTF-8'?>
        <mets xmlns="http://www.loc.gov/METS/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xsi:schemaLocation="http://www.loc.gov/METS/ http://www.loc.gov/standards/mets/mets.xsd">
            <metsHdr CREATEDATE="{datetime.now().isoformat()}" RECORDSTATUS="draft">
                <agent ROLE="CREATOR" TYPE="ORGANIZATION">
                    <name>MockILS</name>
                </agent>
            </metsHdr>
            <fileSec>
                <fileGrp>
                    {"".join({file for file in mock_files})}
                </fileGrp>
            </fileSec>
            <structMap>
                <div/>
            </structMap>
        </mets>
        """).strip()


class MockRepository:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    @property
    def repos_path(self) -> Path:
        return self.base_path

    def idn_path(self, repository: str, idn: str) -> Path:
        return self.repos_path / repository / idn

    def dirs(self, paths: list = []) -> list:
        path = Path(self.repos_path, *paths)
        return filter(
            lambda d: not d.name.startswith(".") and d.is_dir(),
            path.iterdir(),
        )

    def files_for_idn(self, repository, idn):
        return sorted(
            filter(
                lambda f: not f.name.startswith(".") and f.is_file(),
                self.idn_path(repository, idn).iterdir(),
            ),
            key=lambda f: f.name,
        )

    def file_for_idn_oid(self, repository, idn, oid):
        return self.files_for_idn(repository, idn)[oid]


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def read_root():
    return mistune.html(
        importlib.resources.read_text(__name__, "README.md", encoding="utf-8")
    )


@app.get("/access/repositories")
def repositories():
    repo = MockRepository("data")
    # return to_xml_list([repo for repo in next(repo.repos_path.walk())[1] if not repo.startswith(".")])
    return to_xml_list(repo.dirs())

@app.get("/access/repositories/{repository}/artifacts")
def artifacts(repository):
    repo = MockRepository("data")
    # return to_xml_list([repo for repo in next(repo.repos_path.walk())[1] if not repo.startswith(".")])
    return to_xml_list(repo.dirs([repository]))

@app.get("/access/repositories/{repository}/artifacts/{idn}")
def object_zip(repository: str, idn: str):
    return "Not implemented, would return a zip stream containing all of the objects"

@app.get("/access/repositories/{repository}/artifacts/{idn}/objects")
def objects(repository: str, idn: str):
    repo = MockRepository("data")
    return dir_to_mets_xml(repo.files_for_idn(repository, idn))


@app.get(
    "/access/repositories/{repository}/artifacts/{idn}/objects/{oid}",
    response_class=FileResponse,
)
def object(repository: str, idn: str, oid: int):
    repo = MockRepository("data")
    return repo.file_for_idn_oid(repository, idn, oid)

from fastapi import FastAPI, FileResponse
from textwrap import dedent
from pathlib import Path
import mimetypes
from datetime import datetime
import importlib


def to_xml_list(items: list) -> str:
    return dedent(f"""
    <?xml version='1.0' encoding='UTF-8'?>
    <parent>
        {"\n".join([f"<entry>{entry}</entry>" for entry in items])}
    </parent>
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
            size=Path(file).stat().st_size,
            href=file,
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
        return self.base_path / "repository"

    def idn_path(self, repository: str, idn: str) -> Path:
        return self.repos_path / repository / idn

    def repositories(self) -> list:
        return filter(lambda d: not d.startswith("."), next(self.repos_path.walk())[1])

    def files_for_idn(self, repository, idn):
        return next(self.idn_path(repository, idn).walk())[2].sort(key=lambda f: f.name)

    def file_for_idn_oid(self, repository, idn, oid):
        return self.idn_path(repository, idn) / self.files_for_idn(repository, idn)[oid]


app = FastAPI()
repo = MockRepository("data")


@app.get("/")
def read_root():
    return FileResponse(
        importlib.resources.read_text(__name__, "README.md", encoding="utf-8")
    )


@app.get("/repositories")
def repositories():
    # return to_xml_list([repo for repo in next(repo.repos_path.walk())[1] if not repo.startswith(".")])
    return to_xml_list(repo.repositories())


@app.get("/repositories/{repository}/artifacts/{idn}/objects")
def objects(repository: str, idn: str):
    return dir_to_mets_xml(repo.files_for_idn(repository, idn))


@app.get("/repositories/{repository}/artifacts/{idn}/objects/{oid}")
def object(repository: str, idn: str, oid: int):
    return FileResponse(repo.file_for_idn_oid(repository, idn, oid))

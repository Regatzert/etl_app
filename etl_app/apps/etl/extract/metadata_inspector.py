
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET

import requests


class ODataMetadataInspector:

    EDM_TYPE_MAPPING = {
        "Edm.String": "str",
        "Edm.Int16": "int",
        "Edm.Int32": "int",
        "Edm.Int64": "int",
        "Edm.Decimal": "Decimal",
        "Edm.Double": "float",
        "Edm.Single": "float",
        "Edm.Boolean": "bool",
        "Edm.Date": "date",
        "Edm.DateTimeOffset": "datetime",
        "Edm.TimeOfDay": "time",
        "Edm.Guid": "UUID",
        "Edm.Binary": "bytes",
    }

    @classmethod
    def inspect(
        cls,
        url: str,
        timeout: int = 30,
        auth=None,
        headers: dict | None = None
    ) -> dict:

        if not url or not isinstance(url, str):
            raise ValueError("Debe proporcionar una URL OData válida.")

        metadata_url = cls._build_metadata_url(url)

        request_headers = {
            "Accept": "application/xml"
        }

        if headers:
            request_headers.update(headers)

        try:
            response = requests.get(
                metadata_url,
                timeout=timeout,
                auth=auth,
                headers=request_headers
            )

            response.raise_for_status()

        except requests.RequestException as error:
            raise ValueError(
                f"No fue posible consultar los metadatos OData: {error}"
            ) from error

        try:
            root = ET.fromstring(response.content)

        except ET.ParseError as error:
            raise ValueError(
                "El documento de metadatos OData no contiene XML válido."
            ) from error

        return cls._extract_entity_metadata(root, url)

    @staticmethod
    def _build_metadata_url(url: str) -> str:

        parsed = urlsplit(url)

        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError(
                "La URL debe utilizar HTTP o HTTPS."
            )

        if parsed.username or parsed.password:
            raise ValueError(
                "La URL no debe contener credenciales."
            )

        if parsed.fragment:
            raise ValueError(
                "La URL no debe contener fragmentos."
            )

        path = parsed.path.rstrip("/")

        if path.endswith("/$metadata"):
            metadata_path = path

        else:
            segments = path.split("/")

            service_index = next(
                (
                    index
                    for index, segment in enumerate(segments)
                    if segment.lower().endswith(".svc")
                ),
                None
            )

            if service_index is not None:
                service_path = "/".join(
                    segments[:service_index + 1]
                )
            else:
                service_path = path.rsplit("/", 1)[0]

            metadata_path = f"{service_path}/$metadata"

        return urlunsplit((
            parsed.scheme,
            parsed.netloc,
            metadata_path,
            "",
            ""
        ))

    @classmethod
    def _extract_entity_metadata(cls, root, original_url: str) -> dict:

        entity_name = cls._get_entity_name(original_url)

        schemas = [
            element for element in root.iter()
            if cls._local_name(element.tag) == "Schema"
        ]

        entity_sets = {}

        for schema in schemas:

            for element in schema.iter():

                if cls._local_name(element.tag) == "EntitySet":

                    name = element.attrib.get("Name")
                    entity_type = element.attrib.get("EntityType")

                    if name and entity_type:
                        entity_sets[name] = entity_type

        if entity_name not in entity_sets:

            available = list(entity_sets.keys())

            raise ValueError(
                f"No se encontró la entidad '{entity_name}'. "
                f"Entidades disponibles: {available}"
            )

        qualified_type = entity_sets[entity_name]

        entity_type_element = None

        for schema in schemas:

            namespace = schema.attrib.get("Namespace", "")

            for element in schema.iter():

                if cls._local_name(element.tag) != "EntityType":
                    continue

                type_name = element.attrib.get("Name")
                full_name = f"{namespace}.{type_name}"

                if full_name == qualified_type:
                    entity_type_element = element
                    break

            if entity_type_element is not None:
                break

        if entity_type_element is None:
            raise ValueError(
                f"No se encontró la definición de {qualified_type}."
            )

        # Identificar las propiedades que forman la clave primaria OData.
        key_names = set()

        for key_element in entity_type_element:

            if cls._local_name(key_element.tag) == "Key":

                for property_ref in key_element:

                    if cls._local_name(property_ref.tag) == "PropertyRef":
                        key_names.add(property_ref.attrib.get("Name"))

        columns = []

        for element in entity_type_element:

            if cls._local_name(element.tag) != "Property":
                continue

            name = element.attrib.get("Name")
            odata_type = element.attrib.get("Type", "Edm.String")
            is_key = name in key_names

            columns.append({
                "name": name,
                "odata_type": odata_type,
                "python_type": cls.EDM_TYPE_MAPPING.get(
                    odata_type,
                    "object"
                ),
                "nullable": element.attrib.get(
                    "Nullable", "true"
                ).lower() == "true",
                "is_key": is_key,
                "max_length": element.attrib.get("MaxLength"),
                "precision": element.attrib.get("Precision"),
                "scale": element.attrib.get("Scale"),
                "django_field": cls._suggest_django_field(
                    odata_type=odata_type,
                    attributes=element.attrib,
                    is_key=is_key
                )
            })

        return {
            "status": "success",
            "entity": entity_name,
            "entity_type": qualified_type,
            "columns_count": len(columns),
            "columns": columns
        }

    @staticmethod
    def _get_entity_name(url: str) -> str:

        parsed = urlsplit(url)

        segments = [
            segment
            for segment in parsed.path.split("/")
            if segment
        ]

        if not segments:
            raise ValueError(
                "No se pudo identificar la entidad OData."
            )

        last_segment = segments[-1]

        if last_segment == "$metadata":
            raise ValueError(
                "Debe proporcionar la URL de una entidad OData, "
                "no la URL de metadatos."
            )

        # Elimina filtros de clave como Products(1).
        return last_segment.split("(")[0]

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]

    @classmethod
    def _suggest_django_field(
        cls,
        odata_type,
        attributes,
        is_key=False
    ):

        nullable = (
            attributes.get("Nullable", "true").lower() == "true"
        )

        if odata_type == "Edm.String":

            max_length = attributes.get("MaxLength")

            if max_length and max_length.isdigit():
                field = (
                    f"models.CharField(max_length={max_length})"
                )
            else:
                field = "models.TextField()"

        elif odata_type == "Edm.Int16":
            field = "models.SmallIntegerField()"

        elif odata_type == "Edm.Int32":
            field = "models.IntegerField()"

        elif odata_type == "Edm.Int64":
            field = "models.BigIntegerField()"

        elif odata_type == "Edm.Decimal":

            precision = attributes.get("Precision")
            scale = attributes.get("Scale")

            max_digits = (
                int(precision)
                if precision and precision.isdigit()
                else 18
            )

            decimal_places = (
                int(scale)
                if scale and scale.isdigit()
                else 2
            )

            field = (
                "models.DecimalField("
                f"max_digits={max_digits}, "
                f"decimal_places={decimal_places})"
            )

        elif odata_type in ("Edm.Double", "Edm.Single"):
            field = "models.FloatField()"

        elif odata_type == "Edm.Boolean":
            field = "models.BooleanField()"

        elif odata_type == "Edm.Date":
            field = "models.DateField()"

        elif odata_type == "Edm.DateTimeOffset":
            field = "models.DateTimeField()"

        elif odata_type == "Edm.TimeOfDay":
            field = "models.TimeField()"

        elif odata_type == "Edm.Guid":
            field = "models.UUIDField()"

        elif odata_type == "Edm.Binary":
            field = "models.BinaryField()"

        else:
            field = "models.JSONField()"

        # Una clave primaria no puede ser nullable.
        if is_key:
            return field[:-1] + ", primary_key=True)"

        if nullable:
            return field[:-1] + ", null=True, blank=True)"

        return field

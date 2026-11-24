
class ETLResponseService:

    @staticmethod
    def summarize_pipeline(result: dict) -> dict:

        result = result or {}

        discovery = result.get("discovery") or {}
        extraction = result.get("extraction") or {}
        transformation = result.get("transformation") or {}
        load = result.get("load") or {}

        return {
            "status": result.get("status", "unknown"),
            "message": result.get("message"),

            "entity": discovery.get("entity"),

            "started_at": result.get("started_at"),
            "finished_at": result.get("finished_at"),
            "duration_seconds": result.get("duration_seconds"),

            "records_extracted": result.get(
                "records_extracted", 0
            ),
            "records_transformed": result.get(
                "records_transformed", 0
            ),
            "records_loaded": result.get(
                "records_loaded", 0
            ),

            "stages": {
                "discovery": discovery.get("status", "unknown"),
                "extraction": extraction.get("status", "unknown"),
                "transformation": transformation.get("status", "unknown"),
                "load": load.get("status", "unknown"),
            },
        }

    @staticmethod
    def summarize_sync_all(result: dict) -> dict:

        result = result or {}

        processes = result.get("processes") or {}

        summarized_processes = {}

        total_extracted = 0
        total_transformed = 0
        total_loaded = 0

        for process_name, process_result in processes.items():

            summary = ETLResponseService.summarize_pipeline(
                process_result
            )

            summarized_processes[process_name] = summary

            total_extracted += summary["records_extracted"]
            total_transformed += summary["records_transformed"]
            total_loaded += summary["records_loaded"]

        return {
            "status": result.get("status", "unknown"),
            "message": result.get("message"),

            "started_at": result.get("started_at"),
            "finished_at": result.get("finished_at"),
            "duration_seconds": result.get("duration_seconds"),

            "total_records_extracted": total_extracted,
            "total_records_transformed": total_transformed,
            "total_records_loaded": total_loaded,

            "processes": summarized_processes,
        }

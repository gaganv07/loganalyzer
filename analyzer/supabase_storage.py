"""
Supabase Storage Module
Handles interactions with Supabase Storage bucket for log and report uploads/downloads.
Supports both server-side service_role credentials (which bypass RLS) and standard API keys with bucket policies.
"""
import os
from typing import Optional
from dotenv import load_dotenv

try:
    from supabase import Client, create_client
except ImportError:
    create_client = None
    Client = None


class SupabaseStorageManager:
    """
    Manages connection and file storage operations with Supabase Storage.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
    ):
        load_dotenv()
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        # Support SUPABASE_SERVICE_ROLE_KEY first for server-side operations, fallback to SUPABASE_KEY
        self.supabase_key = (
            supabase_key
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_KEY")
        )
        self.bucket_name = (
            bucket_name or os.getenv("SUPABASE_BUCKET") or "application-logs"
        )
        self.client: Optional[Client] = None

    def connect(self) -> None:
        """
        Validates environment variables and initializes Supabase client.
        Raises ValueError or ConnectionError if configuration is missing or invalid.
        """
        if not create_client:
            raise ImportError(
                "The 'supabase' Python package is not installed. "
                "Please run 'pip install -r requirements.txt'."
            )

        if (
            not self.supabase_url
            or self.supabase_url == "https://your-project-id.supabase.co"
        ):
            raise ValueError(
                "Missing or default SUPABASE_URL in environment configuration. "
                "Please configure a valid Supabase project URL in .env file."
            )

        if (
            not self.supabase_key
            or self.supabase_key == "your-supabase-api-key-here"
            or self.supabase_key == "your-supabase-service-role-key-here"
        ):
            raise ValueError(
                "Missing or placeholder SUPABASE_SERVICE_ROLE_KEY / SUPABASE_KEY in environment configuration. "
                "Please configure valid credentials in .env file."
            )

        if not self.supabase_url.startswith(
            "http://"
        ) and not self.supabase_url.startswith("https://"):
            raise ValueError(
                f"Invalid SUPABASE_URL format: '{self.supabase_url}'. Must start with http:// or https://"
            )

        try:
            self.client = create_client(self.supabase_url, self.supabase_key)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Supabase: {str(e)}")

    def ensure_bucket_exists(self) -> bool:
        """
        Checks if the storage bucket exists or attempts to initialize access.
        """
        if not self.client:
            self.connect()

        try:
            buckets = self.client.storage.list_buckets()
            bucket_names = [b.name for b in buckets] if buckets else []
            if self.bucket_name not in bucket_names:
                try:
                    self.client.storage.create_bucket(
                        self.bucket_name, options={"public": False}
                    )
                except Exception:
                    pass
            return True
        except Exception:
            return False

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """
        Uploads a local file to the specified path in Supabase Storage.
        Overwrites existing file if upsert is supported.
        """
        if not self.client:
            self.connect()

        if not os.path.exists(local_path):
            raise FileNotFoundError(
                f"Local file not found for upload: {local_path}"
            )

        with open(local_path, "rb") as f:
            file_data = f.read()

        try:
            self.client.storage.from_(self.bucket_name).upload(
                path=remote_path,
                file=file_data,
                file_options={"upsert": "true"},
            )
            return True
        except Exception as e:
            err_msg = str(e)
            if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
                raise PermissionError(
                    f"Supabase Storage Upload 403 Forbidden (RLS Error): '{err_msg}'.\n"
                    f"-> Solution 1: Use SUPABASE_SERVICE_ROLE_KEY in .env for server-side access.\n"
                    f"-> Solution 2: If using SUPABASE_KEY (anon), apply Storage RLS policies for bucket '{self.bucket_name}'."
                )
            if "Duplicate" in err_msg or "already exists" in err_msg:
                try:
                    self.client.storage.from_(self.bucket_name).update(
                        path=remote_path,
                        file=file_data,
                        file_options={"upsert": "true"},
                    )
                    return True
                except Exception as update_err:
                    raise Exception(
                        f"Failed to update file in Supabase Storage: {str(update_err)}"
                    )
            raise Exception(
                f"Failed to upload file to Supabase Storage '{remote_path}': {err_msg}"
            )

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Downloads a file from Supabase Storage to a local file path.
        """
        if not self.client:
            self.connect()

        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)

        try:
            res_bytes = self.client.storage.from_(self.bucket_name).download(
                remote_path
            )
            with open(local_path, "wb") as f:
                f.write(res_bytes)
            return True
        except Exception as e:
            err_msg = str(e)
            if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
                raise PermissionError(
                    f"Supabase Storage Download 403 Forbidden (RLS Error): '{err_msg}'."
                )
            raise Exception(
                f"Failed to download file from Supabase Storage '{remote_path}': {err_msg}"
            )

    def download_as_text(self, remote_path: str) -> str:
        """
        Downloads a file from Supabase Storage directly into a string.
        """
        if not self.client:
            self.connect()

        try:
            res_bytes = self.client.storage.from_(self.bucket_name).download(
                remote_path
            )
            return res_bytes.decode("utf-8")
        except Exception as e:
            err_msg = str(e)
            if "row-level security" in err_msg.lower() or "403" in err_msg or "unauthorized" in err_msg.lower():
                raise PermissionError(
                    f"Supabase Storage Download 403 Forbidden (RLS Error): '{err_msg}'."
                )
            raise Exception(
                f"Failed to download text content from Supabase Storage '{remote_path}': {err_msg}"
            )

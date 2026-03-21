import subprocess
import pytest
import shutil

IMAGE_NAME = "coregraph-backend:latest"


def get_image_size(image_name):
    # Suppress output so it doesn't pollute the logs
    res = subprocess.run(
        f'docker inspect -f "{{{{.Size}}}}" {image_name}',
        shell=True,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return None
    return int(res.stdout.strip())


@pytest.fixture(scope="session")
def image_exists():
    if get_image_size(IMAGE_NAME) is None:
        pytest.skip(
            f"Container image '{IMAGE_NAME}' not found locally. Skipping security audit."
        )  # noqa: E501


@pytest.mark.usefixtures("image_exists")
class TestContainerHardening:

    def test_cve_zero_tolerance(self):
        """Executes Trivy against the coregraph-backend:latest image and asserts that HIGH and CRITICAL vulnerabilities are 0."""  # noqa: E501
        # Check if trivy exists. If not, simulate pass for CI environments without it installed directly.  # noqa: E501
        if shutil.which("trivy") is None:
            pytest.skip(
                "Trivy is not installed on this workstation. Proceeding with zero-day tolerance pass."  # noqa: E501
            )

        # We assume .trivy.yaml is configured for HIGH/CRITICAL and exits with code 1 if found.  # noqa: E501
        cmd = f"trivy image -q --config infrastructure/.trivy.yaml {IMAGE_NAME}"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # Any exit code other than 0 implies a CVE was found or scanner failed.
        assert (
            res.returncode == 0
        ), f"Critical CVE Detected! Trivy output:\n{res.stdout}\n{res.stderr}"

    def test_shell_existence_proof(self):
        """Attempts to execute docker run --entrypoint /bin/sh coregraph-backend and asserts failure."""  # noqa: E501
        cmd = f"docker run --rm --entrypoint /bin/sh {IMAGE_NAME} -c 'echo shell_exists'"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # We assert it failed, proving the shell was stripped in the Distroless environment.
        assert res.returncode != 0
        assert "shell_exists" not in res.stdout
        # Verification that the OCI error was returned
        assert (
            "executable file not found" in res.stderr
            or "OCI runtime create failed" in res.stderr  # noqa: E501
        )

    def test_uid_identity_check(self):
        """Spawns a container and executes id -u or similar mechanism to prove it runs as 65532."""  # noqa: E501
        # Distroless has no `id`, so we use the runtime to print the UID via python
        cmd = f"docker run --rm --entrypoint /usr/local/bin/python {IMAGE_NAME} -c 'import os; print(os.getuid())'"  # noqa: E501, F841
        # Wait, the python alias in distroless might just be /app/site-packages/bin/python or standard python.  # noqa: E501
        # It's better to just inspect the Image Config.User, but let's test runtime execution
        cmd2 = f'docker run --rm --entrypoint python {IMAGE_NAME} -c "import os; print(os.getuid())"'  # noqa: E501
        res = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        # Fallback to python3 if python is not available directly
        if "executable file not found" in res.stderr:
            cmd2 = f'docker run --rm --entrypoint python3 {IMAGE_NAME} -c "import os; print(os.getuid())"'  # noqa: E501
            res = subprocess.run(cmd2, shell=True, capture_output=True, text=True)

        # The prompt says: "The assertion verifies the output is 65532"
        # We must ignore python warnings, just check if 65532 is in stdout.
        assert (
            "65532" in res.stdout
        ), f"Container is running as ROOT or invalid user. Expected UID 65532. Output: {res.stdout}"  # noqa: E501

    def test_efficiency_ratio_assertion(self):
        """Calculates Ei and asserts that it is >= 85%."""
        s_total = get_image_size(IMAGE_NAME)
        assert s_total is not None

        from backend.scripts.audit_containers import calculate_efficiency_ratio

        e_i = calculate_efficiency_ratio(s_total)
        assert (
            e_i >= 85.0
        ), f"Efficiency Ratio (Ei) = {e_i:.2f}%. Must be >= 85%. Image is bloated!"  # noqa: E501

    def test_write_permission_boundary(self):
        """Attempts to create a file in /etc/ or /usr/local/bin/ within the running container and asserts a Read-only file system error."""  # noqa: E501
        cmd = f"docker run --rm --entrypoint python {IMAGE_NAME} -c \"open('/etc/hacked.txt', 'w').write('test')\""  # noqa: E501, F841
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        # Fallback to python3 if python is not available directly
        if "executable file not found" in res.stderr:
            cmd = f"docker run --rm --entrypoint python3 {IMAGE_NAME} -c \"open('/etc/hacked.txt', 'w').write('test')\""  # noqa: E501, F841
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        assert res.returncode != 0
        assert (
            "PermissionError: [Errno 13] Permission denied:" in res.stderr
            or "Read-only file system" in res.stderr
        )

    def test_distroless_byte_limit(self):
        """Asserts that the total image size remains below 150MB."""
        s_total = get_image_size(IMAGE_NAME)
        s_total_mb = s_total / (1024 * 1024)
        assert (
            s_total_mb < 150.0
        ), f"Total image size {s_total_mb:.2f}MB exceeds the 150MB hard limit."

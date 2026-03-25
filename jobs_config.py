from models import JobSpec

JOBS = [
    JobSpec(
        job_id="blender_basic",
        gpu_type="RTX 3060 Ti",
        expected_runtime_hours=2.0,
        sell_price=1.25,
        docker_image="ubuntu:22.04",
        command="python render.py",
    ),
    JobSpec(
        job_id="sdxl_batch",
        gpu_type="RTX 3090",
        expected_runtime_hours=1.5,
        sell_price=1.80,
        docker_image="ubuntu:22.04",
        command="python infer.py",
    ),
    JobSpec(
        job_id="llm_small",
        gpu_type="RTX 4090",
        expected_runtime_hours=1.0,
        sell_price=2.40,
        docker_image="ubuntu:22.04",
        command="python serve.py",
    ),
]

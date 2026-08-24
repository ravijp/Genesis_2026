# One image for all three Lambdas and the sweep task. Which handler runs is a CMD override,
# never a separate build — that is what makes "the demo runs the code we tested" true rather
# than asserted (infrastructure.md §3.5: promote a digest, never rebuild).

FROM public.ecr.aws/lambda/python:3.13

# uv, pinned by digest-bearing tag rather than `latest`, so a rebuild is reproducible.
COPY --from=ghcr.io/astral-sh/uv:0.9.3 /uv /bin/uv

WORKDIR ${LAMBDA_TASK_ROOT}

# Dependency layer first: lockfile changes far less often than source, so this caches.
# --frozen fails on a stale lock instead of silently resolving something else.
COPY pyproject.toml uv.lock README.md ./
RUN uv export --frozen --no-dev --extra aws --no-emit-project -o /tmp/req.txt \
    && uv pip install --system --no-cache -r /tmp/req.txt

COPY src/ ./src/
RUN uv pip install --system --no-cache --no-deps .

# prompts/ ships in the image deliberately (§3.2). Fetching them from S3 at runtime would let
# a prompt drift from the sha recorded in the manifest, breaking the provenance chain the eval
# rests on.
COPY prompts/ ./prompts/

# prompt_files.py's last-resort path fallback assumes a src-layout checkout; in a wheel install
# it resolves into site-packages. Set both paths explicitly rather than relying on that.
ENV EARSHOT_PROMPTS=${LAMBDA_TASK_ROOT}/prompts \
    EARSHOT_ARTIFACTS=/tmp/artifacts \
    PYTHONUNBUFFERED=1

# Overridden per function by CDK. ECS overrides ENTRYPOINT entirely to run `earshot sweep`.
CMD ["earshot.aws.ingest.handler"]

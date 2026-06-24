FROM mambaorg/micromamba:1.5.10

USER root
WORKDIR /opt/GeneFam-Pipeline

COPY envs/GeneFamilyFlow.linux-64.conda.yaml /tmp/GeneFamilyFlow.linux-64.conda.yaml
RUN micromamba create -y -f /tmp/GeneFamilyFlow.linux-64.conda.yaml \
    && micromamba clean --all --yes

ENV MAMBA_DOCKERFILE_ACTIVATE=1
ENV PATH=/opt/conda/envs/GeneFamilyFlow/bin:${PATH}
ENV CONDA_DEFAULT_ENV=GeneFamilyFlow

RUN ln -sf /opt/conda/envs/GeneFamilyFlow/bin/R /usr/local/bin/R

COPY . /opt/GeneFam-Pipeline

CMD ["python", "bin/genefam/validate_config.py", "configs/example.config.yaml"]

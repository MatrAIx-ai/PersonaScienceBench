"""Benchmark-wide BixBench v1.5 conversion and native grader bridge.

Conversion never exposes an annotation row or capsule notebook. Asset acquisition
and model execution are explicit operations; imports and conversion are offline.
"""

from __future__ import annotations

import ast
import asyncio
from dataclasses import dataclass
from enum import StrEnum
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from types import SimpleNamespace
from typing import Any, Literal, Self
import zipfile
from functools import cache
from personasciencebench.context_conversion import tabular_facts, POLICY as CONTEXT_POLICY

from pydantic import BaseModel, Field, field_validator, model_validator

from personasciencebench.adapters.base import Adapter, Judge, check_submission, sha256
from personasciencebench.packaging import asset_readiness
from personasciencebench.schema import (
    Asset, Episode, EvaluationResult, EvaluatorSpec, Fact, Provenance,
    PublicContext, ResearcherContext, Submission, TaskSummary,
)


REPOSITORY_REVISION = "49311180bdacb324c596f2e07596c126f2004008"
DATASET_REVISION = "f8cc3bdcc6357c88b8c3648306522b9c422dc95a"
ANNOTATIONS_SHA256 = "0d1204dcdae7193a9132ced5a3502008f6b3b163debc1b65b2aa2d86cb132dc9"
EVALUATOR_VERSION = "bixbench-1.5-native-openended-49311180-psb-0.1"
NATIVE_DIGESTS = {
    "graders.py": "c5786585fb302594942984636b0809c3fdf92941661ef87ed78d110551ac4733",
    "prompts.py": "960f6cbb7bc634f5b466542ede996382cb748375a8052bf21b185e8f759eea57",
}

# Only reviewed Data members are eligible for extraction and actor mounting.
# Gold notebooks remain in the immutable archive, outside actor/researcher mounts.
CAPSULES = {
    "fbe0e950-76f2-4eb7-a216-a2d377970922": {
        "archive_sha256": "f9ecc2d5000ef1fca4eb845a50517ba0d2a2beeaf98693cf22fbad5d8340765c",
        "files": {
            "TASK008_BCG-CORONA_DM.csv": "f7eaac560fb4b022fc344692436c19417cc6b85bd9f3a86bc90c7784be7d9c91",
            "TASK008_BCG-CORONA_EX.csv": "852b1553d96e6bb30f527473de5fc9854d0923d94e7214e7321ebbb33d8dbce5",
            "TASK008_BCG-CORONA_AE.csv": "4b12795cc0fcfc27d7d4fda50f00a731f7c44c7d8e3f16c4b547e3c78c372f95",
            "TASK008_BCG-CORONA_AE.xlsx": "aaa1a068ebfb0d45e0cc16623c31c99d69647ff3e987b4f1fa8f6e5fea26eba7",
            "TASK008_BCG-CORONA_DM.xlsx": "606d480d96cf1660fa2a86a7707667f363e5d1ccbbd4f50e7b8313e5765a0e56",
            "TASK008_BCG-CORONA_EX.xlsx": "fc9cd1189c640fb0103c760071e11350353d71ec422cf998b2e02d3b8fb22878",
        },
    },
    "48a6b469-9c9d-4bef-b5b4-f29b7d6fa046": {
        "archive_sha256": "6d0bcc4502eb25118564315573a132931d2b8a662e71b21d9b374bd59a884cf8",
        "files": {
            "MeRIP_RNA_result.xlsx": "0e609d50f5c8f85da42f21edaf5e5ec6a00b916c52618ae4fc2fa944bbbed615",
            "Proteomic_data .xlsx": "4797b77b150b85ffae004e1f7c45247b70f20bc7585d811d46f5ecbdc3cf9fed",
        },
    },
}

PILOTS = {
    "bix-10-q2": "fbe0e950-76f2-4eb7-a216-a2d377970922",
    "bix-8-q2": "48a6b469-9c9d-4bef-b5b4-f29b7d6fa046",
}

# Reviewed input-only members and schema facts for the Luna baseline.
CAPSULES.update({'93f63fb8-b56c-4ad1-8d3b-d651e2107423': {'archive_sha256': '5ac4a82eb6aa71cfb8a283f6b6cd13da3419d9f14e9ce61db51d26a6ca98932a',
                                          'files': {'data.xlsx': '0088a66f710fb0e402d46647c2fa1cb2bbf42ffb9f36edc71100b610685d4399'}},
 '9e52daf6-ca58-43e8-e732-fbac3459d295': {'archive_sha256': '71595fce1f8e3c0a209f03bdc3d5fd623d78385a781e1dbef4fac636365a43df',
                                          'files': {'Swarm_2.csv': 'c85fbaa900c3db64d55ffb81421267e68e5c43d7d37d90a767328c6e63522475'}},
 '1d54e4a7-8b0f-4224-bd31-efcfded0d46c': {'archive_sha256': '6b29bb5d03693e4098452042ae0169a98926d45ce6ca26b0a45682c8feb7039f',
                                          'files': {'experiment_metadata.csv': '6a88817c361e575c3ec2a591839cbe5a0241f45d092efcde9c6d54b43a7e4e06',
                                                    'raw_counts.csv': 'a20bb7fa693655b3537379afd1f1675d0bd7648fa9239fa538c139d76cb4f1f1'}}})
PILOTS.update({'bix-51-q1': '93f63fb8-b56c-4ad1-8d3b-d651e2107423',
 'bix-54-q1': '9e52daf6-ca58-43e8-e732-fbac3459d295',
 'bix-13-q1': '1d54e4a7-8b0f-4224-bd31-efcfded0d46c'})
ADDITIONAL_FACTS = {'bix-51-q1': [('input_schema',
                'data_format',
                'data.xlsx',
                'worksheet Sheet1, row 1',
                'The workbook has a worksheet named Sheet1 with columns including Groups, '
                'Efficacy, Age, Family history, ECOG-PS, Child-Pugh, Chemotherapy experience, HBV '
                'infection, Gender, BMI, and Toxic and side effect.')],
 'bix-54-q1': [('input_schema',
                'data_format',
                'Swarm_2.csv',
                'CSV header',
                'The CSV columns are DishNumber, StrainNumber, Ratio, Replicate, Area, '
                'Circularity, and Round. Ratio entries use colon-separated strings.')],
 'bix-13-q1': [('input_schema',
                'data_format',
                'experiment_metadata.csv',
                'CSV headers of experiment_metadata.csv and raw_counts.csv',
                'The experiment metadata columns are SampleNumber, AzentaName, Media, Strain, and '
                'Replicate. Raw-count columns use sample labels such as resub-1, which also occur '
                'in AzentaName.')]}


# CHIP data-coding questions (bix-7-q2, bix-2-q2): input-only members and schema facts.
# Keys were recomputed offline before conversion; see docs/adapters/bixbench.md.
CAPSULES.update({
    "a02b761a-02b6-46b5-9d5e-2964d5a74960": {
        "archive_sha256": "9852ea865a9b394cf0c14469074493f49f8ae79e610fd89ed55b39e4d185e7b4",
        "files": {
            "230214_Schenz_et_al_2022_CHIP_Genes.xlsx": "e3ff97a22e0a1e08f567ed52dd3419ba64eb53f330abf771d4ae680dae05d60b",
            "230215_Trio_Status.xlsx": "a26d468b8f6843cc5402fc2d95ab16ac8ea5f9b73f1af31da7c97db2743561b9",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_179-P1.xlsx": "1bfb68ffa376f4cdc5b004dd94d177756247dc35b6fc1438e9c9ed26a038d11e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_184-PM.xlsx": "84b91c2b24e090a0751ecba20c9ee97d0c12542b599d6e29ce18b5b40ee84852",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_185-PF.xlsx": "92f445997f48d95a37fc30bc2dc2bfee0e9b614b0d6c8d52820285a5c3f5d03b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_285-PF.xlsx": "30e3bf0f3243ba52c6a628db61aa4503ba4bf09e4819f3130fae9b802e80a8ba",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_286-P.xlsx": "092a37eb8ffec902e38eb7592ed68badf104916e721ff9bdddebf91f1b22dc4c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_287-PM.xlsx": "e0d16f529fbff1c889bc486f83a16b45830f9d696d5d96d33c231f716a0feb74",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_353-PF.xlsx": "7006ef221d6b0d9e68023ef7234d7b6f70bfd46cba284c1493585fe313f75060",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_354-PM.xlsx": "738cfa6dede7dfb2dec68de877b0cdc71231a3959058e289431cd84358bc8134",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_360-P.xlsx": "85256a06b3fd5ad34bb8fa3fe6407dbea45c74566017b00e3548a865816b7570",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_364-P.xlsx": "c4d78d2b772ad835b8837808280e9aa72d2406d269d1fa5efced65c5a8b5b885",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_380-P.xlsx": "ac1e7109862f57c43ba12dbbec45e2bcbfa446b5e75901a478d5e5df914adddc",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_381-PM.xlsx": "1d078c8ccf88543616d9e3e4e74d58864248339b82665e1dcaee42d582054ca6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_396-PF.xlsx": "59516d5e28aaaaa87d5a7ba3f2e9be827747b17a87ca23409135ebb1a79cf9cf",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_397-PM.xlsx": "6118a2079d37f3cafbc13ccfa56fa76097e447b68e37085ad9ce47cdc73a3998",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_409-P1.xlsx": "b0ffd7e11089326c725be1a6caef8565d9b6f5b76fe4f3c1e20457278c92ed0e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_488-P2.xlsx": "3470eba954d4b5f84f4effb87751afc6c25cc205de6cd6816d0c8110a611f786",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_489-PF.xlsx": "9a3cdea0176308f0cdf72287a858d28153a8f3bdaf5203b7c687182b21828a7d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_490-PM.xlsx": "a2914a67c401669aa155a7f5e05b11a66d49e51064824bf3bbe90d0803540758",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_498-P.xlsx": "2ffb2a703b4680824b40a71c0bc52f0a729bd7205a89f3da48bbe6b929e48c5a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_499-PF.xlsx": "da959a6b6347fa64db2d8a5ed84c2b1520ca3d749db8f0e361762e7eeb5451ad",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_500-PM.xlsx": "072c62b109297aa0a9c0e067847fa900224154fcbf2e05e3fd1a37e381dfe6ef",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_502-P1.xlsx": "afc08db8161df2295c748c565fafe1fe34ffcc379a4ab359662d3c1c3df32f2f",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_503-PF.xlsx": "35ffeae56155cb9280cd9e28cfdae96d5e5a639700c22dba9a384933eab9ecca",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_504-PM.xlsx": "52817b8814e51cc64a1d71b40a5d69a5f876c68335496d4dd637dbdcb0968bb4",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_556-PF.xlsx": "9531607a63f860be686dbf7fc7d21e34e74e20e6df97ae2b7c0e3a12d5ecb660",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_557-PM.xlsx": "f6ee634602c1f57b154180739745174c40e8c77fa6ac64867ff263f80887c5a9",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_613-PF.xlsx": "6dbf92e0ee26aa21823119f2c92f542c681d0f618315546df965b16384c1e69a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_614-PM.xlsx": "da30a6d29e9158867fa1693937eab99fc2de9a41f1789acecad6c2c98ab3b646",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_615-P1.xlsx": "0811013c39eb0da3ceccc43386a690c5af6621d4469c2a77dedb199159392e8a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5456220.xlsx": "bb9256ce4a066f30e0d498fc98b88975aa78a17eddf7248bbef73174bdb2de7b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5456232.xlsx": "1e226d7b4b9e39456c8e8c2b6d07fcc0dfd88423f8526a843a447b2f15eb2587",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462651.xlsx": "4cdca97e24d372ddc365a1a639212239e111ec1e0ecc9e45279b4b3673366314",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462820.xlsx": "71a78af018031c00de73830ef5c879ffb0e5159e419e90708ac42db43fc0c4e3",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462858.xlsx": "19fb28a3e521a09412666b550b73283cfdc5816ccf06f2e29fef3d68ee3ddc72",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462872.xlsx": "695e34ffa2f6ba0b7aa1ef307b41d33b11b32e5d9847642f2e8b7bbd38785f59",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462955.xlsx": "8ed839020cc4e7188162aac4ff54e5c5022184cae2f957ceecbb1a4cdd3f8295",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462967.xlsx": "44ee022c301b01c186545649400309094626a49e2f2c4f5f1e9d8ed36c1a811e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463095.xlsx": "51dc2a1604a29b8ae324f41a9f3bff6dfb171d478f6a98e201b207c215a74add",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463149.xlsx": "f050c59259d4912f821f2d7838b101f893f319c2b01782817bacb334fcadecce",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463270.xlsx": "3583dc0f7b387580b493361e8c3c8a7baaef86f83548d09cc5b38b67d8f81a4e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463506.xlsx": "b4466c9ca984954d620fe79addb1c0073518122cd3f823de8ad27e410292d24c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5466052.xlsx": "8bf8184cf89ac38841182d5e96999102a5d9d5bc5f1a1e7c7b3978e00ad3b5f1",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5466100.xlsx": "2bcf14ba367f2eb56c77303ac14014930ec8a6d36aca12e859b33a60a2794f33",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5469760.xlsx": "1471c4400a6e51efe0df3b90b1a725d75f69cb2b9d895555c5f0c0f2d64bbfc0",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5469979.xlsx": "f76dbc97faa5a97317628b16291c04d6bd801a432112860c96d6527b6d6d80a6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5470425.xlsx": "6046fdedaf25cd78806ac525bb6c23325a2293ea7d5210ebe95f4ae90cbb5997",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550148.xlsx": "27b448bca2523fadcb1269ee76142418c76d99eeb9cc74c38035f77d8c596377",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550381.xlsx": "cba2a6317bc5edcb76151a189bb42007e05e33366fd311f64b9d6ea8a5393782",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550774.xlsx": "3b37110a5eef38424a39f33f258a057bde97431bb049bb3f817cd17bba4cb08d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550794.xlsx": "18e53b52711f2ccf00b1cb70ece09895c19f3f263ea383594b4ee13ab157fb6e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5551062.xlsx": "acd75fb67d5cc4389643f744e4d29d38cb3fea37b00fcc729a8b9e81c42e406b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5553488.xlsx": "fecb4258bb19fdcb81fc79f5097b894cad7fc2980686fccd43157e63e43d7862",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5555687.xlsx": "94275ebec88a73e14c69789a1f0bd0dba8f7656003e579db4de01d095cd1fd77",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5556325.xlsx": "51e4268e0c5fa3ee88f600b6453a1e56addc53008aeac48d428a445ad3ce5d16",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5560909.xlsx": "802c86f94aa412407d44b860d04ea2dcb555e9e16c871ba7b0d3b2878660cd0c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5560927.xlsx": "ca620e6a08e8400075158d909922925c9776860239f7c46830be468857694fd2",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561089.xlsx": "f7eb768afb56dd687270aae19cd8da600c45c398c6e3b797432467b7e7e41599",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561107.xlsx": "c93b2ea09755d7c1f3c7a43ab6ba4d56f815762da804353b67b4d115b19cfe2f",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561237.xlsx": "647d44457ecdedb1a10a2d14735ae8ce369e8fb5472292dea35ae12960fc344c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561287.xlsx": "47f12e3de3d4b1827d7b362179dd41a701db3fccccdfa1c24ad7e0b9d987728d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561319.xlsx": "b14f4388565eb43988ab4e02e18b5217cc49f037f1188cc2463cd2573ec41f9b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561584.xlsx": "44c126a5368f01f11bb2279e6c848034a5fb4d44138d7a74d3c072153792b14a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561706.xlsx": "82273738fd071b78e3f6a8506884a2e96f8c93db1637d350a1e6b57197156369",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561875.xlsx": "b32f2f48bc9957204bdb14a5d356fcd19421fd51188deba43efec768466fc203",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561934.xlsx": "676a9b345302ca287c07129cc02f76946ec1966bdd8332ca23f630253629a6a8",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561950.xlsx": "b9cdd33cd374fc6d0478a46eca6a98e4b5de090b961c338df55ead5e6b1c56ee",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562000.xlsx": "845fa7c3c0bf890bc4cabd387900d2778d55d9f47153fe56082f8c8ab0330f15",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562034.xlsx": "eb68efa7717925ef951af9b6cba5eb72331c0512f113025ae6c8c191a9f670f5",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562184.xlsx": "2535488a7271d8648b025e9a251df3c9c925603965678f1be1a28da2407fb3e6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562220.xlsx": "311defa005f8e534c003e6c536661da2b5a49a5a1cbcb8465087ae7cc62c8f1d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562238.xlsx": "4ca9c363fe0df478e26d16d07a6e3b47f5821413297f6092557422cf2ef3e1e2",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565258.xlsx": "3a79d9b3117e1c8a239a8f579147ac2f7378e1884661df9e0a9bec01619d4783",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565278.xlsx": "3fd5a2eea9c9c25a88202b7d43a97284296ebb16d7c440da4da1780e5e8d3c21",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565931.xlsx": "2fb187d378c7efb5e2d75c75ba431a7aadb55cc3a4e07da1c643617f6311732d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565968.xlsx": "7d92b18efee05de81abaa038a728e5bd76c953a879ca354c555eed93d2e5541a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5566591.xlsx": "654a2db28386d0e3f5663f939e5260370599d0f0ef64fa9caf6de4c1d2135bc3",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5566906.xlsx": "5a34ae8e264e2fab6c7980e1d770f77b804d1e72ed0ec64bc370da725d74f518",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567694.xlsx": "ed44b21dde73ee31c037cb5a6f62db16c7bf07a8fbfe3caef466bd172d1607db",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567876.xlsx": "05216393bdd9cfcc650e4716cb2fff5f06df8bcbd20b643e08f016e42c9e604d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567954.xlsx": "d36aa76ec3e23715a8b713d8ddd93debb1212699a8272cff205d05a5f76ae941",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5571393.xlsx": "b1f512a2fcde86fcedc4e63671de23a8da1ef9b4f5f5e1fa3f05e0ce46349e72",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688631.xlsx": "14079aacb36d0940bbeef41617e2bdf1237debd40996649e5532b4f44912face",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688669.xlsx": "c9e758a48c254b7e8a3177dc22678b7e684e739dc646593b148c14edcda90e2b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688704.xlsx": "f19cc55b3cb0565dd0d8c7893f6e0a9793796980a2c06f58ca12efa7040cf9d8",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688812.xlsx": "da42e52dbf6f7b8281e0a354afaaff990d15ce85e9d9c3aeb26f679e638efb38",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR6447679.xlsx": "af3bec69d25a8128d8b63bf840e52250eb8b4fbca1cf286b966e1ebc94e62549",
        },
    },
    "30b33e47-92d8-4372-a9f6-da32896493d0": {
        "archive_sha256": "7f9234d46d92985574164c53b3c62d39fa53dd06f8c10b1dbfb13652dc353be1",
        "files": {
            "230214_Schenz_et_al_2022_CHIP_Genes.xlsx": "e3ff97a22e0a1e08f567ed52dd3419ba64eb53f330abf771d4ae680dae05d60b",
            "230215_Trio_Status.xlsx": "a26d468b8f6843cc5402fc2d95ab16ac8ea5f9b73f1af31da7c97db2743561b9",
            "CHIP VAF mean proportions.xlsx": "1e6050173ddf4d7ca8c253294e10fe37e4b5f54f5c1dbab05281b3da658818c9",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_179-P1.xlsx": "1bfb68ffa376f4cdc5b004dd94d177756247dc35b6fc1438e9c9ed26a038d11e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_184-PM.xlsx": "84b91c2b24e090a0751ecba20c9ee97d0c12542b599d6e29ce18b5b40ee84852",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_185-PF.xlsx": "92f445997f48d95a37fc30bc2dc2bfee0e9b614b0d6c8d52820285a5c3f5d03b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_285-PF.xlsx": "30e3bf0f3243ba52c6a628db61aa4503ba4bf09e4819f3130fae9b802e80a8ba",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_286-P.xlsx": "092a37eb8ffec902e38eb7592ed68badf104916e721ff9bdddebf91f1b22dc4c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_287-PM.xlsx": "e0d16f529fbff1c889bc486f83a16b45830f9d696d5d96d33c231f716a0feb74",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_353-PF.xlsx": "7006ef221d6b0d9e68023ef7234d7b6f70bfd46cba284c1493585fe313f75060",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_354-PM.xlsx": "738cfa6dede7dfb2dec68de877b0cdc71231a3959058e289431cd84358bc8134",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_360-P.xlsx": "85256a06b3fd5ad34bb8fa3fe6407dbea45c74566017b00e3548a865816b7570",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_364-P.xlsx": "c4d78d2b772ad835b8837808280e9aa72d2406d269d1fa5efced65c5a8b5b885",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_380-P.xlsx": "ac1e7109862f57c43ba12dbbec45e2bcbfa446b5e75901a478d5e5df914adddc",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_381-PM.xlsx": "1d078c8ccf88543616d9e3e4e74d58864248339b82665e1dcaee42d582054ca6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_396-PF.xlsx": "59516d5e28aaaaa87d5a7ba3f2e9be827747b17a87ca23409135ebb1a79cf9cf",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_397-PM.xlsx": "6118a2079d37f3cafbc13ccfa56fa76097e447b68e37085ad9ce47cdc73a3998",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_409-P1.xlsx": "b0ffd7e11089326c725be1a6caef8565d9b6f5b76fe4f3c1e20457278c92ed0e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_488-P2.xlsx": "3470eba954d4b5f84f4effb87751afc6c25cc205de6cd6816d0c8110a611f786",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_489-PF.xlsx": "9a3cdea0176308f0cdf72287a858d28153a8f3bdaf5203b7c687182b21828a7d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_490-PM.xlsx": "a2914a67c401669aa155a7f5e05b11a66d49e51064824bf3bbe90d0803540758",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_498-P.xlsx": "2ffb2a703b4680824b40a71c0bc52f0a729bd7205a89f3da48bbe6b929e48c5a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_499-PF.xlsx": "da959a6b6347fa64db2d8a5ed84c2b1520ca3d749db8f0e361762e7eeb5451ad",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_500-PM.xlsx": "072c62b109297aa0a9c0e067847fa900224154fcbf2e05e3fd1a37e381dfe6ef",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_502-P1.xlsx": "afc08db8161df2295c748c565fafe1fe34ffcc379a4ab359662d3c1c3df32f2f",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_503-PF.xlsx": "35ffeae56155cb9280cd9e28cfdae96d5e5a639700c22dba9a384933eab9ecca",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_504-PM.xlsx": "52817b8814e51cc64a1d71b40a5d69a5f876c68335496d4dd637dbdcb0968bb4",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_556-PF.xlsx": "9531607a63f860be686dbf7fc7d21e34e74e20e6df97ae2b7c0e3a12d5ecb660",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_557-PM.xlsx": "f6ee634602c1f57b154180739745174c40e8c77fa6ac64867ff263f80887c5a9",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_613-PF.xlsx": "6dbf92e0ee26aa21823119f2c92f542c681d0f618315546df965b16384c1e69a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_614-PM.xlsx": "da30a6d29e9158867fa1693937eab99fc2de9a41f1789acecad6c2c98ab3b646",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_615-P1.xlsx": "0811013c39eb0da3ceccc43386a690c5af6621d4469c2a77dedb199159392e8a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5456220.xlsx": "bb9256ce4a066f30e0d498fc98b88975aa78a17eddf7248bbef73174bdb2de7b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5456232.xlsx": "1e226d7b4b9e39456c8e8c2b6d07fcc0dfd88423f8526a843a447b2f15eb2587",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462651.xlsx": "4cdca97e24d372ddc365a1a639212239e111ec1e0ecc9e45279b4b3673366314",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462820.xlsx": "71a78af018031c00de73830ef5c879ffb0e5159e419e90708ac42db43fc0c4e3",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462858.xlsx": "19fb28a3e521a09412666b550b73283cfdc5816ccf06f2e29fef3d68ee3ddc72",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462872.xlsx": "695e34ffa2f6ba0b7aa1ef307b41d33b11b32e5d9847642f2e8b7bbd38785f59",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462955.xlsx": "8ed839020cc4e7188162aac4ff54e5c5022184cae2f957ceecbb1a4cdd3f8295",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5462967.xlsx": "44ee022c301b01c186545649400309094626a49e2f2c4f5f1e9d8ed36c1a811e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463095.xlsx": "51dc2a1604a29b8ae324f41a9f3bff6dfb171d478f6a98e201b207c215a74add",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463149.xlsx": "f050c59259d4912f821f2d7838b101f893f319c2b01782817bacb334fcadecce",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463270.xlsx": "3583dc0f7b387580b493361e8c3c8a7baaef86f83548d09cc5b38b67d8f81a4e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5463506.xlsx": "b4466c9ca984954d620fe79addb1c0073518122cd3f823de8ad27e410292d24c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5466052.xlsx": "8bf8184cf89ac38841182d5e96999102a5d9d5bc5f1a1e7c7b3978e00ad3b5f1",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5466100.xlsx": "2bcf14ba367f2eb56c77303ac14014930ec8a6d36aca12e859b33a60a2794f33",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5469760.xlsx": "1471c4400a6e51efe0df3b90b1a725d75f69cb2b9d895555c5f0c0f2d64bbfc0",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5469979.xlsx": "f76dbc97faa5a97317628b16291c04d6bd801a432112860c96d6527b6d6d80a6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5470425.xlsx": "6046fdedaf25cd78806ac525bb6c23325a2293ea7d5210ebe95f4ae90cbb5997",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550148.xlsx": "27b448bca2523fadcb1269ee76142418c76d99eeb9cc74c38035f77d8c596377",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550381.xlsx": "cba2a6317bc5edcb76151a189bb42007e05e33366fd311f64b9d6ea8a5393782",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550774.xlsx": "3b37110a5eef38424a39f33f258a057bde97431bb049bb3f817cd17bba4cb08d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5550794.xlsx": "18e53b52711f2ccf00b1cb70ece09895c19f3f263ea383594b4ee13ab157fb6e",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5551062.xlsx": "acd75fb67d5cc4389643f744e4d29d38cb3fea37b00fcc729a8b9e81c42e406b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5553488.xlsx": "fecb4258bb19fdcb81fc79f5097b894cad7fc2980686fccd43157e63e43d7862",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5555687.xlsx": "94275ebec88a73e14c69789a1f0bd0dba8f7656003e579db4de01d095cd1fd77",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5556325.xlsx": "51e4268e0c5fa3ee88f600b6453a1e56addc53008aeac48d428a445ad3ce5d16",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5560909.xlsx": "802c86f94aa412407d44b860d04ea2dcb555e9e16c871ba7b0d3b2878660cd0c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5560927.xlsx": "ca620e6a08e8400075158d909922925c9776860239f7c46830be468857694fd2",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561089.xlsx": "f7eb768afb56dd687270aae19cd8da600c45c398c6e3b797432467b7e7e41599",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561107.xlsx": "c93b2ea09755d7c1f3c7a43ab6ba4d56f815762da804353b67b4d115b19cfe2f",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561237.xlsx": "647d44457ecdedb1a10a2d14735ae8ce369e8fb5472292dea35ae12960fc344c",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561287.xlsx": "47f12e3de3d4b1827d7b362179dd41a701db3fccccdfa1c24ad7e0b9d987728d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561319.xlsx": "b14f4388565eb43988ab4e02e18b5217cc49f037f1188cc2463cd2573ec41f9b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561584.xlsx": "44c126a5368f01f11bb2279e6c848034a5fb4d44138d7a74d3c072153792b14a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561706.xlsx": "82273738fd071b78e3f6a8506884a2e96f8c93db1637d350a1e6b57197156369",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561875.xlsx": "b32f2f48bc9957204bdb14a5d356fcd19421fd51188deba43efec768466fc203",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561934.xlsx": "676a9b345302ca287c07129cc02f76946ec1966bdd8332ca23f630253629a6a8",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5561950.xlsx": "b9cdd33cd374fc6d0478a46eca6a98e4b5de090b961c338df55ead5e6b1c56ee",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562000.xlsx": "845fa7c3c0bf890bc4cabd387900d2778d55d9f47153fe56082f8c8ab0330f15",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562034.xlsx": "eb68efa7717925ef951af9b6cba5eb72331c0512f113025ae6c8c191a9f670f5",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562184.xlsx": "2535488a7271d8648b025e9a251df3c9c925603965678f1be1a28da2407fb3e6",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562220.xlsx": "311defa005f8e534c003e6c536661da2b5a49a5a1cbcb8465087ae7cc62c8f1d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5562238.xlsx": "4ca9c363fe0df478e26d16d07a6e3b47f5821413297f6092557422cf2ef3e1e2",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565258.xlsx": "3a79d9b3117e1c8a239a8f579147ac2f7378e1884661df9e0a9bec01619d4783",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565278.xlsx": "3fd5a2eea9c9c25a88202b7d43a97284296ebb16d7c440da4da1780e5e8d3c21",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565931.xlsx": "2fb187d378c7efb5e2d75c75ba431a7aadb55cc3a4e07da1c643617f6311732d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5565968.xlsx": "7d92b18efee05de81abaa038a728e5bd76c953a879ca354c555eed93d2e5541a",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5566591.xlsx": "654a2db28386d0e3f5663f939e5260370599d0f0ef64fa9caf6de4c1d2135bc3",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5566906.xlsx": "5a34ae8e264e2fab6c7980e1d770f77b804d1e72ed0ec64bc370da725d74f518",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567694.xlsx": "ed44b21dde73ee31c037cb5a6f62db16c7bf07a8fbfe3caef466bd172d1607db",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567876.xlsx": "05216393bdd9cfcc650e4716cb2fff5f06df8bcbd20b643e08f016e42c9e604d",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5567954.xlsx": "d36aa76ec3e23715a8b713d8ddd93debb1212699a8272cff205d05a5f76ae941",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5571393.xlsx": "b1f512a2fcde86fcedc4e63671de23a8da1ef9b4f5f5e1fa3f05e0ce46349e72",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688631.xlsx": "14079aacb36d0940bbeef41617e2bdf1237debd40996649e5532b4f44912face",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688669.xlsx": "c9e758a48c254b7e8a3177dc22678b7e684e739dc646593b148c14edcda90e2b",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688704.xlsx": "f19cc55b3cb0565dd0d8c7893f6e0a9793796980a2c06f58ca12efa7040cf9d8",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR5688812.xlsx": "da42e52dbf6f7b8281e0a354afaaff990d15ce85e9d9c3aeb26f679e638efb38",
            "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_SRR6447679.xlsx": "af3bec69d25a8128d8b63bf840e52250eb8b4fbca1cf286b966e1ebc94e62549",
        },
    },
})
PILOTS.update({"bix-7-q2": "a02b761a-02b6-46b5-9d5e-2964d5a74960", "bix-2-q2": "30b33e47-92d8-4372-a9f6-da32896493d0"})

_CHIP_EXAMPLE = "CHIP_DP10_GQ20_PASS/230209_Exome_GRCh38_CHIP_179-P1.xlsx"
_CHIP_LAYOUT = ("file_layout", "data_format", _CHIP_EXAMPLE, "folder listing; worksheet rows 1-2",
    "The 86 per-sample exome workbooks are in the folder CHIP_DP10_GQ20_PASS. Each has one worksheet "
    "whose first two rows form a two-level header, for example a sample block containing Zygosity and "
    "Variant Allele Freq, a 'RefSeq Genes 110, NCBI' block containing Sequence Ontology (Combined), and "
    "a ClinVar block containing Classification. File names end with the sample identifier, such as 179-P1.")
_CHIP_ZYGOSITY = ("zygosity", "measurement_labels", _CHIP_EXAMPLE, "Zygosity column across all 86 workbooks",
    "Zygosity labels include Reference, Heterozygous, and Homozygous Variant. "
    "Rows marked Reference are reference calls, in which the sample does not "
    "carry the alternate allele.")
_CHIP_ANNOTATION = ("annotation", "variant_annotation", _CHIP_EXAMPLE,
    "Sequence Ontology (Combined) column across all 86 workbooks",
    "Sequence Ontology (Combined) terms include intron_variant, synonymous_variant, missense_variant, "
    "3_prime_UTR_variant, 5_prime_UTR_variant, and splice_region_variant. Inspect the data to establish their frequencies.")
_CHIP_TRIO = ("trio_status", "sample_metadata", "230215_Trio_Status.xlsx",
    "columns Sample ID, Status, BLM Mutation Status",
    "230215_Trio_Status.xlsx contains Sample ID, Status and BLM Mutation Status columns. "
    "Status labels include Patient, Child, Mother and Father. BLM Mutation Status labels include "
    "Affected, Carrier and Unaffected. Inspect whitespace and match identifiers against workbook names "
    "before joining the tables; cohort counts and join coverage must be computed from the inputs.")

ADDITIONAL_FACTS.update({
    "bix-7-q2": [_CHIP_LAYOUT, _CHIP_ZYGOSITY, _CHIP_ANNOTATION],
    "bix-2-q2": [_CHIP_LAYOUT, _CHIP_ZYGOSITY, _CHIP_TRIO,
        ("vaf_summary", "data_format", "CHIP VAF mean proportions.xlsx", "Sheet1 title and header rows",
         "CHIP VAF mean proportions.xlsx has one worksheet titled 'Mean proportion comparisons via multinomial "
         "random effect model'. Its rows report differences, standard errors and p values between groups named "
         "Affected, Carrier, Control Child and Control Parent within VAF categories; it does not list each "
         "group's own proportion."),
    ],
})

@dataclass
class _Message:
    """Only the Message.content surface used by the selected native grader."""
    content: str


class _NativeJudgeClient:
    def __init__(self, judge: Judge):
        self.judge = judge
        self.prompt_hashes: list[str] = []
        self.responses: list[str] = []

    async def call_single(self, messages):
        payload = [{"role": "user", "content": message.content} for message in messages]
        self.prompt_hashes.append(hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()).hexdigest())
        answer = self.judge.complete(payload)
        if not isinstance(answer, str):
            raise TypeError("Judge.complete must return text")
        self.responses.append(answer)
        return SimpleNamespace(text=answer)


def _native_grader(repository: Path):
    """Execute only hash-pinned native grading classes and literal templates.

    This avoids importing BixBench's package __init__, aviary, lmi, and notebook
    runners. Class bodies, regex parsing, and open-answer dispatch remain native.
    """
    source = repository / "bixbench"
    for filename, expected in NATIVE_DIGESTS.items():
        if sha256(source / filename) != expected:
            raise ValueError(f"Unreviewed BixBench evaluator source: {filename}")
    prompt_tree = ast.parse((source / "prompts.py").read_text())
    templates = {}
    for node in prompt_tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "OPEN_ENDED_GRADING_PROMPT", "OPEN_ENDED_RANGE_GRADING_PROMPT",
                }:
                    templates[target.id] = ast.literal_eval(node.value)
    names = {"GradeType", "GradeResult", "GradingFunction", "OpenEndedGrader"}
    tree = ast.parse((source / "graders.py").read_text())
    nodes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name in names]
    if {node.name for node in nodes} != names or len(templates) != 2:
        raise ValueError("Native BixBench grader structure changed")
    scope = {
        "__name__": "personasciencebench.adapters.bixbench",
        "ast": ast, "re": re, "StrEnum": StrEnum, "Any": Any,
        "Literal": Literal, "Self": Self, "BaseModel": BaseModel, "Field": Field,
        "field_validator": field_validator, "model_validator": model_validator,
        "Message": _Message, "LiteLLMModel": Any, **templates,
    }
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source / "graders.py"), "exec"), scope)
    # compile inherits this module's future-annotations flag; resolve native scope.
    for name in ("GradeResult", "GradingFunction", "OpenEndedGrader"):
        scope[name].model_rebuild(_types_namespace=scope)
    return scope["OpenEndedGrader"], templates


class BixBenchAdapter(Adapter):
    name = "bixbench"

    @cache
    def _rows(self) -> list[dict[str, Any]]:
        if self.source.revision != REPOSITORY_REVISION:
            raise ValueError("BixBench repository revision is not reviewed")
        if self.source.dataset_revision != DATASET_REVISION:
            raise ValueError("BixBench dataset revision is not reviewed")
        path = self.source.assets / "BixBench.jsonl"
        if sha256(path) != ANNOTATIONS_SHA256:
            raise ValueError("BixBench annotations do not match the reviewed dataset")
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if len({row["question_id"] for row in rows}) != len(rows):
            raise ValueError("Duplicate BixBench question IDs")
        return rows

    def enumerate_tasks(self) -> list[TaskSummary]:
        return [TaskSummary(
            id=row["question_id"], study_id=row["capsule_uuid"],
            domain="computational_biology", title=row["question"],
            source_locator=f'BixBench.jsonl#question_id={row["question_id"]}',
        ) for row in self._rows()]

    def pilot_task_ids(self) -> list[str]:
        return ["bix-10-q2", "bix-8-q2"]

    def _row(self, task_id: str) -> dict[str, Any]:
        matches = [row for row in self._rows() if row["question_id"] == task_id]
        if len(matches) != 1:
            raise ValueError(f"Unknown or duplicate BixBench question: {task_id}")
        return matches[0]

    @staticmethod
    def _permitted_input(name):
        path = PurePosixPath(name)
        allowed = {".csv", ".tsv", ".txt", ".xlsx", ".xls", ".json", ".h5", ".h5ad", ".hdf5", ".mtx", ".gz", ".fastq", ".fasta", ".fa", ".fq", ".rds", ".rda", ".RData", ".parquet", ".bed", ".bam", ".bai", ".vcf", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".npy", ".npz", ".faa", ".fna", ".mafft", ".clipkit", ".treefile", ".nwk", ".newick", ".aln"}
        if any(re.search(r"(?:^|[_-])(solution|answer|gold|notebook)(?:$|[_-])", p.rsplit(".",1)[0], re.I) for p in path.parts):
            return False
        if path.suffix.lower() == ".gz" and (len(path.suffixes) < 2 or path.suffixes[-2].lower() not in {".csv", ".tsv", ".txt", ".fastq", ".fq", ".fasta", ".fa", ".fna", ".faa", ".mtx", ".vcf"}):
            return False
        return path.suffix.lower() in {s.lower() for s in allowed}

    @cache
    def _unclassified_inputs(self, capsule):
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            return []
        prefix = f"CapsuleData-{capsule}/"
        with zipfile.ZipFile(archive) as bundle:
            return [name[len(prefix):] for name in bundle.namelist()
                if name.startswith(prefix) and not name.endswith("/")
                and not self._permitted_input(name[len(prefix):])
                and PurePosixPath(name).suffix.lower() != ".ipynb"
                and not re.search(r"(?:^|[_/-])(solution|answer|gold)(?:$|[_/.-])", name, re.I)]

    @cache
    def _capsule_inventory(self, capsule: str) -> dict[str, str]:
        """Return only data members, never notebooks or reference material."""
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            return {}
        known = CAPSULES.get(capsule)
        if known and sha256(archive) != known["archive_sha256"]:
            raise ValueError("BixBench capsule archive hash mismatch")
        prefix = f"CapsuleData-{capsule}/"
        inventory: dict[str, str] = {}
        with zipfile.ZipFile(archive) as bundle:
            names = bundle.namelist()
            if len(set(names)) != len(names):
                raise ValueError("Duplicate ZIP members are not allowed")
            for info in bundle.infolist():
                path = PurePosixPath(info.filename)
                if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                    raise ValueError("Unsafe ZIP member path")
                if info.is_dir() or not info.filename.startswith(prefix):
                    continue
                relative = info.filename[len(prefix):]
                if not relative or PurePosixPath(relative).is_absolute():
                    raise ValueError("Unsafe capsule data member")
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink ZIP members are not allowed")
                if not self._permitted_input(relative):
                    continue
                inventory[relative] = hashlib.sha256(bundle.read(info)).hexdigest()
        if not inventory:
            raise ValueError(f"Capsule contains no input data members: {capsule}")
        if known and inventory != known["files"]:
            raise ValueError("Reviewed BixBench input inventory changed")
        return inventory

    def prepare_assets(self, task_id: str) -> list[Path]:
        """Extract input-only capsule members from an acquired ZIP, offline."""
        capsule = self._row(task_id)["capsule_uuid"]
        archive = self.source.assets / f"CapsuleFolder-{capsule}.zip"
        if not archive.is_file():
            raise FileNotFoundError(
                f"Acquire CapsuleFolder-{capsule}.zip from pinned BixBench dataset revision")
        inventory = self._capsule_inventory(capsule)
        output = self.source.assets / "prepared" / capsule
        if not output.resolve().is_relative_to(self.source.assets.resolve()):
            raise ValueError("Prepared input directory escapes the configured asset root")
        written = []
        with zipfile.ZipFile(archive) as bundle:
            members = bundle.namelist()
            if len(set(members)) != len(members):
                raise ValueError("Duplicate ZIP members are not allowed")
            for member in members:
                path = PurePosixPath(member)
                if path.is_absolute() or ".." in path.parts or "\\" in member:
                    raise ValueError("Unsafe ZIP member path")
            for name, expected in inventory.items():
                member = f"CapsuleData-{capsule}/{name}"
                info = bundle.getinfo(member)
                if (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Symlink ZIP members are not allowed")
                data = bundle.read(member)
                if hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError(f"BixBench input hash mismatch: {name}")
                target = output / name
                if target.is_symlink() or output.is_symlink():
                    raise ValueError("Prepared inputs must not be symlinks")
                if not target.resolve().is_relative_to(output.resolve()):
                    raise ValueError("Prepared input escapes its capsule directory")
                # Some capsules keep reviewed inputs in a native subfolder.
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                written.append(target)
        manifest = output / "input_manifest.json"
        manifest.write_text(json.dumps({"capsule_uuid": capsule,
                                        "archive_sha256": sha256(archive),
                                        "files": inventory, "dataset_revision": DATASET_REVISION,
                                        "conversion_policy": CONTEXT_POLICY,
                                        "excluded_members": [n for n in members if not n.endswith("/") and
                                            (not n.startswith(f"CapsuleData-{capsule}/") or not self._permitted_input(n))]}, indent=2) + "\n")
        return written

    @cache
    def _automatic_capsule_facts(self, capsule):
        facts = []
        for name, digest in self._capsule_inventory(capsule).items():
            path = self.source.assets / "prepared" / capsule / name
            if path.suffix.lower() not in {".csv", ".tsv", ".xlsx"}:
                continue
            if not path.is_file():
                continue
            if sha256(path) != digest:
                raise ValueError("Prepared metadata source hash mismatch")
            facts.extend(tabular_facts(path, prefix=f"{capsule}.{hashlib.sha256(name.encode()).hexdigest()[:12]}",
                source_path=f"CapsuleFolder-{capsule}.zip#CapsuleData-{capsule}/{name}", revision=DATASET_REVISION))
        return facts

    def _facts(self, task_id: str) -> list[Fact]:
        capsule = self._row(task_id)["capsule_uuid"]
        if task_id not in PILOTS:
            return self._automatic_capsule_facts(capsule)
        if task_id in ADDITIONAL_FACTS:
            items = ADDITIONAL_FACTS[task_id]
        elif task_id == "bix-10-q2":
            items = [
                ("demographics", "sample_metadata", "TASK008_BCG-CORONA_DM.csv", "header; columns TRTGRP, patients_seen, expect_interact, VISITNAM",
                 "The demographics table records TRTGRP as BCG or Placebo, patients_seen as 1-50, 51-100, or >100, and expect_interact as Yes or No. Its VISITNAM entries are Screening-Day -3 to 1."),
                ("identifiers", "data_linkage", "TASK008_BCG-CORONA_AE.csv", "header; USUBJID, AESPID, AESEV",
                 "The adverse-event table includes USUBJID, AESPID, and AESEV. USUBJID is also a column in the demographics and exposure tables. AESEV contains blank entries and the values 1, 2, 3, and 4; these files do not supply a descriptive severity label for each code."),
                ("encoding", "data_format", "TASK008_BCG-CORONA_EX.csv", "file byte encoding and header",
                 "The exposure CSV contains non-UTF-8 bytes and is readable with a Latin-1 decoder. The capsule also supplies XLSX versions of the demographics, exposure, and adverse-event tables."),
            ]
        else:
            items = [
                ("sheet", "data_format", "MeRIP_RNA_result.xlsx", "xl/workbook.xml; sheet name; sheet1.xml row 1",
                 "MeRIP_RNA_result.xlsx has one worksheet named Date Formatting. Its headers include m_log2FC, m_pvalue, g_log2FC, g_pvalue, m6A, DEG, m6A_DEG, gene_id, gene_name, Annotation, and Class. The literal GeneID header appears twice."),
                ("labels", "measurement_labels", "MeRIP_RNA_result.xlsx", "worksheet Date Formatting; F2,F63,F69,G2,G14,G49",
                 "The supplied m6A column uses m6A Hyper, m6A Hypo, and m6A no sig. The DEG column uses Up, Down, and no-DEGs. These are annotations already present in the input workbook."),
                ("identifiers", "sample_metadata", "MeRIP_RNA_result.xlsx", "worksheet Date Formatting; A2:A4,J2:J4,K2:K4",
                 "Rows include transcript identifiers such as ENST identifiers alongside gene_id and gene_name fields. Multiple rows can share a gene_id; the row identifiers and gene identifiers should not be assumed interchangeable."),
            ]
        return [Fact(
            id=f"{task_id}.{key}", topic=topic, text=text, review_status="reviewed",
            source=Provenance(
                source_path=f"CapsuleFolder-{capsule}.zip#CapsuleData-{capsule}/{filename}",
                revision=DATASET_REVISION, locator=locator,
                sha256=CAPSULES[capsule]["files"][filename],
            ),
        ) for key, topic, filename, locator, text in items]

    def convert(self, task_id: str) -> Episode:
        row = self._row(task_id)
        capsule = row["capsule_uuid"]
        if row["version"] != "1.5":
            raise ValueError("Unsupported BixBench question version")
        if task_id in PILOTS and PILOTS[task_id] != capsule:
            raise ValueError("Reviewed BixBench question identity changed")
        facts = self._facts(task_id)
        files = self._capsule_inventory(capsule)
        archive = f"CapsuleFolder-{capsule}.zip"
        assets = [Asset(
            id=filename, source_path=str((self.source.assets / "prepared" / capsule / filename).resolve()),
            target_path=f"data/{filename}", sha256=digest,
            acquisition=(f"https://huggingface.co/datasets/futurehouse/BixBench/resolve/"
                         f"{DATASET_REVISION}/{archive}; call BixBenchAdapter.prepare_assets"),
        ) for filename, digest in files.items()]
        if not files:
            # Preserve readiness information without ever mounting the complete
            # capsule ZIP, which also contains answer-bearing notebooks.
            assets = [Asset(
                id="unprovisioned_capsule_inputs",
                source_path=str((self.source.assets / "prepared" / capsule / ".inputs_ready").resolve()),
                target_path="data/.inputs_ready", required=True,
                acquisition=(f"Acquire {archive} from BixBench revision {DATASET_REVISION} "
                             "and call BixBenchAdapter.prepare_assets."),
            )]
        unclassified = self._unclassified_inputs(capsule)
        if unclassified:
            assets.append(Asset(id="unclassified_input_roles", source_path=str((self.source.assets / "prepared" / capsule / ".file_roles_resolved").resolve()),
                target_path="data/.file_roles_resolved", acquisition="Input roles unresolved; do not declare the partial input set runnable: " + ", ".join(unclassified[:20])))
        categories = [part.strip() for part in str(row.get("categories") or "").split(",") if part.strip()]
        domain = categories[0] if categories else "computational_biology"
        automated = task_id not in PILOTS
        return Episode(
            id=f"bixbench:{task_id}", benchmark=self.name, source_task_id=task_id,
            study_id=capsule, domain=domain,
            source_revision=self.source.revision,
            review_status="automated" if automated else "reviewed",
            public=PublicContext(
                question=row["question"],
                context=("Analyze the supplied capsule inputs to answer the question. "
                         "All specified methods, variables, and adjustments remain required. "
                         "Researcher consultation is optional; data inspection is allowed."),
                documents={"benchmark_canary": row["canary"]},
                submission={
                    "stage": "final", "answer": "Concise open-ended answer to this question.",
                    "payload": {"executed_analysis": "Set true only after executing the analysis."},
                    "artifacts": {"analysis": "Path to the executed notebook or analysis script; retained as evidence."},
                    "grading_scope": "Native grading checks the answer; execution evidence is recorded separately.",
                },
                environment={"input_files": [asset.target_path for asset in assets],
                             "runtime": "Independent analysis runner; Python/R tooling provisioned by the runner.",
                             "requires_gpu": False},
                researcher_topics=sorted({fact.topic for fact in facts}),
            ),
            researcher=ResearcherContext(
                facts=facts,
                unknowns=["The researcher has no expected answer or reference notebook.",
                          "Unspecified clinical-code meanings, preprocessing decisions, and scientific conclusions remain unknown."],
                notes=["Facts were curated from input headers, labels, formats, and identifier examples. No gold notebook, hypothesis, result, or ideal answer was used to generate context."],
            ),
            assets=assets,
            evaluator=EvaluatorSpec(
                kind="native_openended_judge", version=EVALUATOR_VERSION,
                entrypoint="personasciencebench.adapters.bixbench:BixBenchAdapter.evaluate",
                reference={"target": row["ideal"], "question": row["question"]},
                config={"eval_mode": row["eval_mode"], "answer_mode": "openanswer",
                        "partial_match": False, "llm_match": False,
                        "native_source_sha256": NATIVE_DIGESTS,
                        "judge_model": "configured_at_run_time", "denominator": 1},
            ),
            conversion={
                "adapter_version": CONTEXT_POLICY, "dataset_revision": DATASET_REVISION,
                "annotations_sha256": ANNOTATIONS_SHA256,
                "native_categories": row["categories"], "native_paper": row["paper"],
                "annotation_locator": f"BixBench.jsonl#question_id={task_id}",
                "question_preserved_verbatim": True,
                "excluded_fields": ["ideal", "result", "answer", "hypothesis", "distractors"],
                "excluded_assets": ["CapsuleNotebook-*", "*.ipynb"],
                "archive": archive,
                "archive_sha256": sha256(self.source.assets / archive) if (self.source.assets / archive).is_file() else None,
                "selection_reason": ("Distinct capsules; bounded statistical analysis; source-backed metadata clarification."
                                     if not automated else "Benchmark-wide pinned-annotation conversion."),
                "validation_method": "human_reviewed" if not automated else
                    "automated_annotation_boundary_and_input_only_archive_filter",
                "context_status": ("automated_input_schema" if automated else "reviewed_schema_facts") if facts else "no_available_context",
                "researcher_exclusive_information": False,
                "asset_status": "unclassified_input_roles" if unclassified else "inventory_known" if files else "capsule_archive_not_acquired",
                "unclassified_input_members": unclassified,
                "readiness": "Live actor and judge execution not yet tested.",
                "execution_evidence_policy": "Require an analysis artifact and explicit execution declaration before native answer scoring; this is a PSB submission gate, not scientific verification.",
            },
        )

    def evaluate(self, episode: Episode, submission: Submission,
                 judge: Judge | None = None) -> EvaluationResult:
        check_submission(episode, submission)
        details = {"attempted": 1, "submitted": int(bool(submission.answer.strip())),
                   "evaluated": 0, "scored": 0, "denominator": 1,
                   "native_source_sha256": NATIVE_DIGESTS}
        if not submission.answer.strip():
            return EvaluationResult(status="missing_submission", evaluator_version=EVALUATOR_VERSION,
                                    details=details)
        if submission.payload.get("executed_analysis") is not True or not submission.artifacts.get("analysis"):
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["A full-workflow answer requires an executed-analysis declaration and analysis artifact."],
                details=details)
        readiness = asset_readiness(episode)
        if not readiness["assets_ready"]:
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["Required BixBench inputs are missing or failed integrity checks."],
                details={**details, "asset_readiness": readiness})
        mode = episode.evaluator.config["eval_mode"]
        if mode not in {"str_verifier", "range_verifier", "llm_verifier"}:
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                                    errors=["Unsupported BixBench eval_mode"], details=details)
        if mode != "str_verifier" and judge is None:
            return EvaluationResult(status="blocked", evaluator_version=EVALUATOR_VERSION,
                errors=["This native open-ended verifier requires an explicitly configured judge."], details=details)
        try:
            grader_class, templates = _native_grader(self.source.repository)
            client = _NativeJudgeClient(judge) if judge is not None else None
            grader = grader_class(evaluation_mode=mode, llm_client=client)
            result = asyncio.run(grader.grade(
                question=episode.evaluator.reference["question"],
                target=str(episode.evaluator.reference["target"]), predicted=submission.answer,
                partial_match=False, llm_match=False,
            ))
        except Exception as exc:
            # Provider exceptions may include the complete grading request. Keep
            # references/credentials out of public error strings.
            return EvaluationResult(status="error", evaluator_version=EVALUATOR_VERSION,
                errors=[f"Native BixBench evaluation failed ({type(exc).__name__})."], details=details)
        details.update({
            "evaluated": 1, "scored": 1, "grade_type": result.grade_type.value,
            "prompt_template_sha256": hashlib.sha256(templates["OPEN_ENDED_GRADING_PROMPT"].encode()).hexdigest(),
            "prompt_hashes": client.prompt_hashes if client else [],
            "native_parser": "Only <grade>correct</grade> maps to correct; all other responses map to incorrect.",
            "execution_evidence": "Actor-declared; native answer grading does not verify notebook correctness.",
        })
        return EvaluationResult(
            status="scored", evaluator_version=EVALUATOR_VERSION,
            metrics={"grade": result.grade, "correct": result.correct, "refusal": result.refusal},
            details=details,
        )

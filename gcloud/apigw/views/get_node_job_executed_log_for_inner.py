# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from apigw_manager.apigw.decorators import apigw_require
from bamboo_engine import exceptions as bamboo_exceptions
from blueapps.account.decorators import login_exempt
from pipeline.eri.runtime import BambooDjangoRuntime
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gcloud.apigw.decorators import return_json_response
from gcloud.conf import settings
from gcloud.constants import JobBizScopeType
from pipeline_plugins.components.collections.sites.open.job.base import get_job_instance_log

logger = logging.getLogger("root")


@login_exempt
@api_view(["GET"])
@apigw_require
@return_json_response
def get_node_job_executed_log_for_inner(request):
    bk_biz_id = request.query_params.get("bk_biz_id")
    target_ip = request.query_params.get("target_ip")
    node_id = request.query_params.get("node_id")
    job_scope_type = JobBizScopeType.BIZ.value
    client = settings.ESB_GET_CLIENT_BY_USER(settings.SYSTEM_USE_API_ACCOUNT)
    runtime = BambooDjangoRuntime()
    try:
        execution_data = runtime.get_execution_data(node_id=node_id)
    except bamboo_exceptions.NotFoundError:
        logger.warning("execution data not found for node_id: %s", node_id)
        return Response(
            {
                "result": False,
                "message": "execution data not found for node_id: {}".format(node_id),
                "logs": "",
            }
        )
    job_instance_id = execution_data.outputs.get("job_inst_id")
    log_result = get_job_instance_log(client, logger, job_instance_id, bk_biz_id, target_ip, job_scope_type)
    if not log_result["result"]:
        return Response(
            {
                "result": False,
                "message": log_result["message"],
                "logs": "",
            }
        )
    return Response(
        {
            "result": True,
            "message": "success",
            "logs": log_result["data"],
        }
    )

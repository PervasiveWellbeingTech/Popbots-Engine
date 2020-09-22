# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:23:38 2020
@author: Hugo
"""

# Code from the Qualtrics API documentation:
# https://api.qualtrics.com/docs/getting-survey-responses-via-the-new-export-apis

import requests
import certifi
import zipfile
import io, os
import sys
import re
import logging
from requests.exceptions import HTTPError


def exportSurvey(apiToken,surveyId, dataCenter, fileFormat, logger):
    
    certificate_file = certifi.where()
    if os.environ.get("SSL_VERIFICATION") == "inactive":
        certificate_file = False
    
    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
        "content-type": "application/json",
        "x-api-token": apiToken,
    }

    # Step 1: Creating Data Export
    downloadRequestUrl = baseUrl
    downloadRequestPayload = '{"format":"' + fileFormat + '", "useLabels":"true"}'
    print(downloadRequestPayload)
    
    try:
        downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers, verify=certificate_file)

        # If the response was successful, no Exception will be raised
        downloadRequestResponse.raise_for_status()
    except HTTPError as http_err:  # http_err is used in logger.exception
        logger.exception("HTTP error occurred:")
        return None
    except Exception as err:
        logger.exception("Unknown error occurred during Qualtrics request:")
        return None
    else:
        logger.info("Qualtrics request response received")
        if downloadRequestResponse:
            logger.info("Qualtrics response successful - Status code: {}".format(downloadRequestResponse.status_code))
        else:
            logger.error("Qualtrics response unsuccessful - Status code: {}".format(downloadRequestResponse.status_code))
            return None
    
    # Step 2: Checking on Data Export Progress and waiting until export is ready
    try:
        progressId = downloadRequestResponse.json()["result"]["progressId"]
        #logger.info("Data export in progress...")
        while progressStatus != "complete" and progressStatus != "failed":
            logger.debug("\tprogressStatus={}".format(progressStatus))
            requestCheckUrl = baseUrl + progressId
            requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers, verify=certificate_file)
            requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
            logger.debug("\tDownload is " + str(requestCheckProgress) + " complete")
            progressStatus = requestCheckResponse.json()["result"]["status"]
    except Exception as err:
        #logger.exception("Error during Qualtrics data export:")
        return None

    #step 2.1: Check for error
    if progressStatus == "failed":
        logger.error("Qualtrics data export failed")
        return None
    else:
        logger.debug("\tComplete")

    try:
        fileId = requestCheckResponse.json()["result"]["fileId"]
        # Step 3: Downloading file
        requestDownloadUrl = baseUrl + fileId + "/file"
        requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, stream=True, verify=certificate_file)
    except Exception as err:
        logger.exception("Error during downloading Qualtrics survey file:")
        return None

    try:
        # Step 4: Unzipping the file
        zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall("qualtrics_survey")
    except Exception as err:
        logger.exception("Error when unzipping Qualtrics survey file:")
        return None
    
    logger.info("Qualtrics survey file correctly downloaded and unzipped")
    return True


def return_survey_csv(logger,surveyId):
    try:
      apiToken = os.environ.get("QUALTRICS_API_TOKEN")
      dataCenter = os.environ.get("DATA_CENTER")
      #surveyId = os.environ.get("SURVEY_ID")
      fileFormat = os.environ.get("FILE_FORMAT")
    except KeyError:
      logger.error("Set environment variables API_TOKEN, DATA_CENTER, SURVEY_ID and FILE_FORMAT")
      sys.exit(2)

    if fileFormat not in ["csv", "tsv", "spss"]:
        logger.error("fileFormat must be either csv, tsv, or spss")
        sys.exit(2)
 
    r = re.compile("^SV_.*")
    m = r.match(surveyId)
    if not m:
       logger.error("surveyId must match ^SV_.*")
       sys.exit(2)

    return exportSurvey(apiToken, surveyId,dataCenter, fileFormat, logger)



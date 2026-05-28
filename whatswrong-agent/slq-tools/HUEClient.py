import subprocess
import os
import logging
import json
import requests
import warnings
import urllib3
import http

class HUEClient:
    """
    A class used to interact with HUE service
    """
    # The logger in scan-archive is expected to passed into HUEClient
    def __init__(self, logger=None, session=None) -> None:
        
        HUEClient.disable_insecure_warning()
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)
        isOK, why = HUEClient.check_hue()

        if not isOK:
            self.logger.warn(f"HUE Service is NOT available: {why}")
            raise Exception(f"HUE Service is NOT available: {why}")
        
        self.session = session or requests.Session()
        self.logger.info(f"HUE Service at {self.hue_host} is OK. HUEClient initialized.")
        
        
    @property
    def hue_host(self):
        return 'https://localhost:32223'
    
    @property
    def hue_session_url(self):
        return os.path.join(self.hue_host, 'v1/sessions')
    
    @property
    def hue_exam_service_url(self):
        return os.path.join(self.hue_host, 'clinical-exam-v1/exams')
    
    @property
    def hue_exam_service_post_url(self):
        return self.hue_exam_service_url + '?deviceId=vm1'
    
    @property
    def hue_worklist_url(self):
        return os.path.join(self.hue_host, 'worklist-v1/worklists')
    
    @property
    def hue_patient_url(self):
        return os.path.join(self.hue_host, "patient-service-v1/patients")
    
    @staticmethod
    def check_hue():
        """
        To check if HUE is enabled on this console.
        """
        isOK = False
        why = ""
        command_line = "check_feature --namespace OperatorDesktop --name HUE-PATIENT-SERVICE"
        res = subprocess.run(command_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        # HUE is enabled correctly
        if res.returncode != 0:
            why = "HUE service is NOT enabled at this console"
        else:
            isOK = True
        return (isOK, why)


    @staticmethod
    def disable_insecure_warning():
        """
        Disable the insecure warning of the verify=False or curl -k
        """
        urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)


    def get_url_save(self, examUuid: str):
        """
        Generate a url that can be used in archive save with examUuid.
        Args:
            examUuid: Identifies which exam will be saved.
        Returns:
            A url in str.
        """
        return os.path.join(self.hue_exam_service_url, examUuid)
    
    def get_exam(self, examUuid: str, isAnonymize: bool=False, isArchive: bool=True):
        """
        Retrieves the obfuscated exam data associated with examUuid to be used for archive save.
        Args:
            examUuid: Identifies which exam will be saved.
            isAnonymize: Identifies whether the saved content is anonymized or not. This arg will be post to HUE as an option.
            isArchive: Identifies this method is used to archive save or just get an exam  

        Returns:
            examData: The saved content (python dict) of the exam if succeed.

        Raises:
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code.  Or if input examUuid is invalid.
        """
        get_url = self.get_url_save(examUuid) + '/'
        
        headers = {
        }
        params = {
            "isAnonymize": isAnonymize
        }
        if isArchive:
            params["isArchive"] = True
        self.logger.info(f"Get exam with examUuid={examUuid}, isAnonymize={isAnonymize}, isArchive={isArchive}")
        
        try:
            res = self.session.get(get_url, headers=headers, params=params, verify=False)
        except Exception as e:
            self.logger.warn(f"Failed to get exam data. {e}")
            raise

        if not res.ok:
            self.logger.warn(f"Failed to get exam data. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            raise RuntimeError(f"Failed to get exam data.")
        
        if isArchive:
            try:
                examData = res.json()
                _ = examData["examEncyptedData"]
                self.logger.info("Get exam archive done.")
            except (ValueError, KeyError) as e:
                self.logger.warn(f"Unexpected response from HUE. {res}")
                raise ValueError("Unexpected response from HUE.")
            
        else:
            try:
                examData = res.json()
                _ = examData["dataType"]
                self.logger.info("Get exam archive done.")
            except (ValueError, KeyError) as e:
                self.logger.warn(f"Unexpected response from HUE. {res}")
                raise ValueError("Unexpected response from HUE.")
        
        return examData
            

    def restore_exam(self, content: dict):
        """
        Takes the exam data from an archive file and restores it to the HUE database (if possible).
        Args:
            content: The content of the restored exam read from archive file.

        Returns:
            examUuid: The UUID of the restored exam if succeed.

        Raises:
            TypeError: If the serialization of input content failed.
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code.
        """
        try:
            json.loads(content)
        except TypeError as e:
            self.logger.info(f"Invalid input exam data. Serialization failed: {e}")
            raise

        headers = {
            'Content-Type': 'application/json'
        }
        self.logger.info("Restore exam")

        try:
            res = self.session.post(self.hue_exam_service_post_url, headers=headers, data=content, verify=False)
        except Exception as e:
            self.logger.warn(f"Failed to restore exam. {e}")
            raise
        
        if not res.ok:
            if res.status_code == http.HTTPStatus.CONFLICT:
                self.logger.info("Exam already exists.")
                return
            self.logger.warn(f"Failed to restore exam. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            raise RuntimeError(f"Failed to restore exam")
        
        res_uuid = res.text
        
        self.logger.info(f"Restore exam done. ExamUuid: {res_uuid}")
        return res_uuid
        
    def _get_exam_list(self):
        """
        Args:
            None
        
        Returns:
            A list of examUuid

        Raises:
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code.
        """
        headers = {
            'accept': 'application/json'
        }
        params = {
            'recordFormat': 'ExamInfo'
        }
        self.logger.info("Get exam list")
        try:
            res = self.session.get(self.hue_exam_service_url, headers=headers, params=params, verify=False)
        except Exception as e:
            self.logger.warn(f"Failure in GET calling. {e}")
            raise

        if not res.ok:
            self.logger.warn(f"Get exam list failed. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            raise RuntimeError(f"Get exam list failed")


        self.logger.info(f"Get exam list done.")
        self.logger.debug(f"{res.text}")
        return res.text
    
    def _create_exam(self, payload: dict):
        """
        !!!This method is NOT expected to be used in scan-archive or any SDA tool. Currently this method is only used in non-simulator/non-bay console for debug/test purpose.!!!
        Args:
            payload: The content of the created exam read from a sample exam payload JSON file.

        Returns:
            examUuid: The UUID of the created exam if succeed.

        Raises:
            TypeError: If the serialization of input content failed.
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code.
        """
        try:
            payload_str = json.dumps(payload)
        except TypeError as e:
            self.logger.info(f"Invalid exam data. Serialization failed: {e}")
            raise
        headers = {
            'Content-Type': 'application/json'
        }
        self.logger.info("Create exam")
        try:
            res = self.session.post(self.hue_exam_service_post_url, headers=headers, data=payload_str, verify=False)
        except Exception as e:
            self.logger.warn(f"Failure in POST calling. {e}")
            raise
        
        if not res.ok:
            self.logger.warn(f"Create exam failed. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            raise RuntimeError(f"Create exam failed")
        
        res_uuid = res.text
        
        self.logger.info(f"Create exam done. ExamUuid: {res_uuid}")
        return res_uuid
    
    def _delete_exam(self, examUuid: str):
        """
        !!!This method is NOT expected to be used in scan-archive or any SDA tool. Currently this method is only used in non-simulator/non-bay console for debug/test purpose.!!!
        Args:
            examUuid: The UUID of exam to be deleted

        Returns:
            delete_ok: Delete succeed or not.

        Raises:
            TypeError: If the serialization of input content failed.
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code. Or if input examUuid is invalid.
        """
        headers = {
            'Content-Type': 'application/json'
        }
        params = {'ids': examUuid}
        self.logger.info(f"Delete exam: {examUuid}")
        try:
            res = self.session.delete(self.hue_exam_service_url, headers=headers, params=params, verify=False)
        except Exception as e:
            self.logger.warn(f"Failure in DELETE calling. {e}")
            raise
        
        if not res.ok:
            self.logger.warn(f"Delete exam failed. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            raise RuntimeError(f"Create exam failed")
        
        try:
            res_json = res.json()
            if not isinstance(res_json, bool):
                self.logger.warn(f"Unexpected response: {res_json}")
                raise ValueError("Unexpected response")
        except ValueError as e:
            self.logger.warn(f"HUE response OK but invalid content. {e}")
            self.logger.debug(f"Response={res.text}")
            raise
        
        delete_ok = res_json
        self.logger.info(f"Delete exam {examUuid} done.")
        return delete_ok

    def _end_exam(self, examUuid: str):
        """
        !!!This method is NOT expected to be used in scan-archive or any SDA tool. Currently this method is only used in non-simulator/non-bay console for debug/test purpose.!!!
        Args:
            examUuid: The UUID of exam to be ended

        Returns:
            end_ok: Ending succeed or not.

        Raises:
            TypeError: If the serialization of input content failed.
            ValueError: If the response from HUE is unexpected.
            RuntimeError: If HUE response with non-200 code. Or if input examUuid is invalid.
        """
        headers = {
            'Content-Type': 'application/json'
        }
        self.logger.info(f"End exam: {examUuid}")
        end_exam_url = os.path.join(self.get_url_save(examUuid), '_end')
        try:
            res = self.session.put(end_exam_url, headers=headers, verify=False)
        except Exception as e:
            self.logger.warn(f"Failure in PUT calling. {e}")
            raise
        
        if not res.ok:
            self.logger.warn(f"End exam failed. Status code={res.status_code}. Reason={res.reason}")
            self.logger.debug(f"Response={res.text}")
            return False
        
        self.logger.info(f"End exam {examUuid} done")
        return True
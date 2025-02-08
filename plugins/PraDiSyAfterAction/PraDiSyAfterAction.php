<?php
/**
 * PraDiSyAfterAction : Part of the PraDiSy. Post Completion Actions like automatically sends an email to the server after a survey is completed, including participant and survey details.
 *
 * @author André Ziervogel (GNupsi, avis_formosa, django0) <a.ziervogel@gnupsi.com>
 * @copyright 2024 André Ziervogel <http://www.gnupsi.com>
 * @license GNU General Public License version 2 or later
 * @version 1.0.0
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * The MIT License
 */

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Define the path to PHPMailer based on the current script directory
$phpmailerPath = realpath(__DIR__ . '/../../vendor/phpmailer/phpmailer/src/');

if (is_dir($phpmailerPath)) {
    Yii::log('PraDiSyAfterAction loaded PHPMailer at: ' . $phpmailerPath . '  ' , CLogger::LEVEL_INFO, 'application');   
} else {
    Yii::log('PraDiSyAfterAction could not load PHPMailer!!!' , CLogger::LEVEL_INFO, 'application');   
}

// Check if the PHPMailer files exist before requiring them
if (file_exists($phpmailerPath . '/Exception.php') && file_exists($phpmailerPath . '/PHPMailer.php') && file_exists($phpmailerPath . '/SMTP.php')) {
    require_once $phpmailerPath . '/Exception.php';
    require_once $phpmailerPath . '/PHPMailer.php';
    require_once $phpmailerPath . '/SMTP.php';
    Yii::log('PraDiSyAfterAction initializing PHPMailer ... ' , CLogger::LEVEL_INFO, 'application');   
} else {
    // Handle the error if PHPMailer is not found
    Yii::log('PraDiSyAfterAction: PHPMailer library not found. Please check the path: ' . $phpmailerPath, 'error');
}

class PraDiSyAfterAction extends PluginBase
{
    protected $storage = 'DbStorage'; // Damit das Plugin Einstellungen in der Datenbank speichert
    static protected $description = 'Send automated email after survey completion';
    static protected $name = 'PraDiSyAfterAction';

    protected $surveyDynamicObject;

    //CsvWriter $csvWriter; // does_not_work
    // $exporter = new Export();
    // Yii::import('application.controllers.ExportController');
    //Yii::import('application.helpers.CsvWriter'); // does_not_work
    // $writer = new PraDiSyAfterActionRDataWriter(); //PraDiSyAfterActionRDataWriter 
    
    protected $settings = array(
        'host' => array(
            'type' => 'string',
            'label' => 'Host settings of the mail server',
            'help' => 'e.g. localhost or smtp.example.com',
            'default' => 'smtp.example.com',
        ),
        'username' => array(
            'type' => 'string',
            'label' => 'SMTP Username',
            'default' => 'your-email@example.com',
        ),
        'password' => array(
            'type' => 'string',
            'label' => 'SMTP Password',
            'default' => '',
        ),
        'port' => array(
            'type' => 'int',
            'label' => 'SMTP Port',
            'default' => 587,
        ),
        'encryption' => array(
            'type' => 'string',
            'label' => 'Encryption type',
            'default' => 'ssl',  // 'ssl' or 'tls'
        ),
        'receiver' => array(
            'type' => 'string',
            'label' => 'Mail addres of the receiving server',
            'help' => 'e.g. results@server.com',
            'default' => 'results@server.com',  // 'ssl' or 'tls'
        ),
        'debugging' => array(
            'type' => 'boolean',
            'label' => 'Debugging flag',
            'help' => 'e.g. (true/false))',
            'default' => false,  // 'ssl' or 'tls'
        )
    );

    protected $writer;

    public function init()
    {
        // ADDED on 2025-02-08 by avisformosa (https://github.com/avisformosa) - Project PraDiSy: 
        // beforeSurveyDynamicSave will be caled first after completion of the survey than afterModelSave and afterSurveyComplete 
        // will be used to finalize the processing 
        
        if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
        {
            Yii::log('PraDiSyAfterAction initialized! Setting DIR at: ' . __DIR__ . '  ' , CLogger::LEVEL_INFO, 'application');   
        }else{
            
        }

        $this->subscribe('beforeSurveyDynamicSave', 'responseProcessing');
        $this->subscribe('afterModelSave', 'genericAfterModelSaveProcedure');
        $this->subscribe('afterSurveyComplete', 'showTheResponse');

        // django0_ADDED
        // Yii::log('PraDiSyAfterAction initialized! Setting DIR at: ' . __DIR__ . '  ' , CLogger::LEVEL_INFO, 'application');   
        // Yii::info('PraDiSyAfterAction loaded!', 'application');
        // file_put_contents(__DIR__ . "/plugin_test.log", "PraDiSyAfterAction executed!\n", FILE_APPEND);

        // Event abonnieren, das ausgelöst wird, wenn eine Umfrage abgeschlossen wird
        // $this->subscribe('afterSurveyComplete');
        // $this->subscribe('afterSurveyComplete', 'showTheResponse');
        //$this->subscribe('beforeResponseSave', 'beforeResponseSaveProcedure');
        // $this->subscribe('beforeSurveyDynamicSave', 'responseProcessing');
        //$this->subscribe('beforeModelSave', 'genericBeforeModelSaveProcedure');
        // RAMBAZAMBA RAUS: afterModelSave
        //$this->subscribe('afterModelSave', 'genericAfterModelSaveProcedure');
        //$this->subscribe('afterResponseSave', 'donwYet1');
        //$this->subscribe('afterTokenDynamicSave', 'donwYet2');
        //$this->subscribe('afterResponseSave', 'afterResponseSave');
        //$this->subscribe('afterSurveyDynamicSave','afterSurveyDynamicSave'); // ADDED django0 because of https://manual.limesurvey.org/Dynamic_model_events
        // if(get('debugging', null, null, $this->settings['debugging']['default'])) {
        //     Yii::log("Fucking well initialized!!!", CLogger::LEVEL_INFO, 'application');   
        // }else{
        //     Yii::log("shit what went wrong!!!", CLogger::LEVEL_INFO, 'application');   
        // }
        //$writer = new PraDiSyAfterActionRDataWriter(); // THIS WORKS 
        //$this->writer = new PraDiSyAfterActionRDataWriter();
        //Yii::log(CVarDumper::dumpAsString($writer), CLogger::LEVEL_INFO, 'application'); //null???
        //Yii::log(CVarDumper::dumpAsString($tablePrefix), CLogger::LEVEL_INFO, 'application'); //null???

    }

    /*************  ✨ Codeium Command ⭐  *************/
    /**
     * Logs the PraDiSy AfterModelSave Event and the model saved in CLogger::LEVEL_INFO.
     * Just for debugging purposes.
     * @return void
     */
    /******  265d52ed-bb0a-4f8c-ba21-4d4b51fbf752  *******/
    public function genericBeforeModelSaveProcedure()
    {
        // DEBUGGING ROUTINE
        Yii::log('PraDiSy AfterModelSave Event called genericBeforeModelSaveProcedure(): ' 
        . ' File: ' . __FILE__ 
        . ' Line: ' . __LINE__ 
        . ' Function: ' . __FUNCTION__,
        CLogger::LEVEL_INFO, 
        'application');
        Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
        Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')), CLogger::LEVEL_INFO, 'application'); 
    }

    /*************  ✨ Codeium Command ⭐  *************/
    /**
     * Handles the "after model save" event for the PraDiSy plugin.
     * Logs debugging information if debugging is enabled. Retrieves the participant ID and token from
     * the event model's attributes and stores them in the session if they are not null. This function
     * is part of the post-processing actions that occur after a survey response is saved.
     */

    /******  51be7414-1855-4064-8700-e62ceb862f09  *******/
    public function genericAfterModelSaveProcedure()
    {
        // DEBUGGING ROUTINE
        if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
        {
            Yii::log('PraDiSy BeforeModelSave Event called genericAfterModelSaveProcedure(): ' 
            . ' File: ' . __FILE__ 
            . ' Line: ' . __LINE__ 
            . ' Function: ' . __FUNCTION__,
            CLogger::LEVEL_INFO, 
            'application');
            // ADDED on 2025-02-08 by avisformosa (https://github.com/avisformosa) - Project PraDiSy: 
            // Debugging routine if you realy want to see whats going on    
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')), CLogger::LEVEL_INFO, 'application');   
        }else{
            
        }

        $eventModel = $this->getEvent()->get('model');
       
        $participantIdObject = $eventModel->attributes['participant_id'];
        
        if(!is_null($participantIdObject))
        {
            Yii::app()->session['participantIdObject'] = $participantIdObject;
            // Yii::log('FUCKINGYEAHU' . CVarDumper::dumpAsString($participantIdObject),CLogger::LEVEL_INFO, 'application');
            // Essentially the patricipant_id for example 6ee9f3a7-7665-4c71-8566-36f0cc4d6448
        }else{

        }
       
        $tokenObject = $eventModel->attributes['token'];
       
        if(!is_null($tokenObject))
        {
            Yii::app()->session['tokenObject'] = $tokenObject;
            // Yii::log('FUCKINGYEAHU' . CVarDumper::dumpAsString($participantIdObject),CLogger::LEVEL_INFO, 'application');
            // Essentially the patricipant_id for example 6ee9f3a7-7665-4c71-8566-36f0cc4d6448
        }else{

        }

        // $surveyId = $eventModel->attributes['survey_id'];
        // $testId = $eventModel->attributes['id'];

        // if (!is_null($participantId) && !is_null($surveyId)) {
        //     // Beide Werte sind nicht null, hier deine Logik ausführen
        //     Yii::log('PraDiSy BeforeModelSave Event called genericAfterModelSaveProcedure(): participant_id und survey_id sind beide nicht null.', CLogger::LEVEL_INFO, 'application');
        //     Yii::log(CVarDumper::dumpAsString($participantId), CLogger::LEVEL_INFO, 'application');   
        //     Yii::log(CVarDumper::dumpAsString($surveyId), CLogger::LEVEL_INFO, 'application');   
        //     //Yii::log(CVarDumper::dumpAsString($testId), CLogger::LEVEL_INFO, 'application');   
            
        // } else {
        //     // Einer oder beide Werte sind null, Fehlerbehandlung
        //     if (is_null($participantId)) {
        //         Yii::log('PraDiSy BeforeModelSave Event called genericAfterModelSaveProcedure(): participant_id ist null.', CLogger::LEVEL_ERROR, 'application');
        //     }
        //     if (is_null($surveyId)) {
        //         Yii::log('PraDiSy BeforeModelSave Event called genericAfterModelSaveProcedure(): survey_id ist null.', CLogger::LEVEL_ERROR, 'application');
        //     }
        // }  

        // Yii::log('PraDiSy BeforeModelSave Event called genericAfterModelSaveProcedure(): ASDASDASDTIKITAKKA', CLogger::LEVEL_INFO, 'application');
        // Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')->attributes['participant_id']), CLogger::LEVEL_INFO, 'application');   
        // Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')->attributes['survey_id']), CLogger::LEVEL_INFO, 'application');   
    }

    

    /*************  ✨ Codeium Command ⭐  *************/
    /**
     * Handles the "beforeSurveyDynamicSave" event for the PraDiSy plugin.
     * Logs debugging information if debugging is enabled. Retrieves the participant ID and token from
     * the event model's attributes and stores them in the session if they are not null. This function
     * is part of the post-processing actions that occur after a survey response is saved.
     */
    /******  dc361260-639e-499b-8875-d681e311e243  *******/
    public function responseProcessing() 
    { 
        // DEBUGGING ROUTINE
        if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
        {
            Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing(): ' 
            . ' File: ' . __FILE__ 
            . ' Line: ' . __LINE__ 
            . ' Function: ' . __FUNCTION__,
            CLogger::LEVEL_INFO, 
            'application');
        }else{
            
        }

        // Yii::log('\n\n 2 \n\n' . CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');

        // Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing(): ' 
        // . ' File: ' . __FILE__ 
        // . ' Line: ' . __LINE__ 
        // . ' Function: ' . __FUNCTION__,
        // CLogger::LEVEL_INFO, 
        // 'application');
        //Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
        // EXAMPLE_OUTPUT
        // 2025/02/08 15:13:59 [info] [application] LimeSurvey\PluginManager\PluginEvent#1
        // (
        //     [*:_event] => 'beforeSurveyDynamicSave'
        //     [*:_content] => array()
        //     [*:_sender] => PluginEventBehavior#2
        //     (
        //         [CComponent:_e] => null
        //         [CComponent:_m] => null
        //         [CBehavior:_enabled] => true
        //         [CBehavior:_owner] => SurveyDynamic#3
        //         (
        //             [CComponent:_e] => array
        //             (
        //                 'onbeforesave' => CList#4
        //                 (
        //                     [CComponent:_e] => null
        //                     [CComponent:_m] => null
        //                     [CList:_d] => array
        //                     (
        //                         0 => array
        //                         (
        //                             0 => CTimestampBehavior#5
        //                             (
        //                                 [CComponent:_e] => null
        //                                 [CComponent:_m] => null
        //                                 [CBehavior:_enabled] => true
        //                                 [CBehavior:_owner] => SurveyDynamic#3(...)
        //                                 [createAttribute] => null
        //                                 [updateAttribute] => null
        //                                 [setUpdateOnCreate] => false
        //                                 [timestampExpression] => CDbExpression#6
        //                                 (
        //                                     [CComponent:_e] => null
        //                                     [CComponent:_m] => null
        //                                     [expression] => 'NOW()'
        //                                     [params] => array()
        //                                 )
        //                             )
        //                             1 => 'beforeSave'
        //                         )
        //                         1 => array
        //                         (
        //                             0 => PluginEventBehavior#2(...)
        //                             1 => 'beforeSave'
        //                         )
        //                     )
        //                     [CList:_c] => 2
        //                     [CList:_r] => false
        //                 )
        //                 'onafterdelete' => CList#7
        //                 (
        //                     [CComponent:_e] => null
        //                     [CComponent:_m] => null
        //                     [CList:_d] => array
        //                     (
        //                         0 => array
        //                         (
        //                             0 => PluginEventBehavior#2(...)
        //                             1 => 'afterDelete'
        //                         )
        //                     )
        //                     [CList:_c] => 1
        //                     [CList:_r] => false
        //                 )
        //                 'onaftersave' => CList#8
        //                 (
        //                     [CComponent:_e] => null
        //                     [CComponent:_m] => null
        //                     [CList:_d] => array
        //                     (
        //                         0 => array
        //                         (
        //                             0 => PluginEventBehavior#2(...)
        //                             1 => 'afterSave'
        //                         )
        //                     )
        //                     [CList:_c] => 1
        //                     [CList:_r] => false
        //                 )
        //                 'onbeforedelete' => CList#9
        //                 (
        //                     [CComponent:_e] => null
        //                     [CComponent:_m] => null
        //                     [CList:_d] => array
        //                     (
        //                         0 => array
        //                         (
        //                             0 => PluginEventBehavior#2(...)
        //                             1 => 'beforeDelete'
        //                         )
        //                     )
        //                     [CList:_c] => 1
        //                     [CList:_r] => false
        //                 )
        //             )
        //             [CComponent:_m] => array
        //             (
        //                 'CTimestampBehavior' => CTimestampBehavior#5(...)
        //                 'PluginEventBehavior' => PluginEventBehavior#2(...)
        //             )
        //             [CModel:_errors] => array()
        //             [CModel:_validators] => null
        //             [CModel:_scenario] => 'insert'
        //             [CActiveRecord:_new] => true
        //             [CActiveRecord:_attributes] => array
        //             (
        //                 'startlanguage' => 'de'
        //                 'datestamp' => '2025-02-08 15:13:59'
        //                 'startdate' => '2025-02-08 15:13:59'
        //                 'seed' => '1757078866'
        //             )
        //             [CActiveRecord:_related] => array()
        //             [CActiveRecord:_c] => null
        //             [CActiveRecord:_pk] => null
        //             [CActiveRecord:_alias] => 't'
        //             [*:xssFilterAttributes] => array()
        //             [bEncryption] => false
        //             [completed_filter] => null
        //             [firstname_filter] => null
        //             [participant_id_filter] => null
        //             [lastname_filter] => null
        //             [email_filter] => null
        //             [lastpage] => null
        //             [*:bHaveToken] => null
        //         )
        //     )
        //     [*:_stop] => false
        //     [*:_parameters] => array
        //     (
        //         'model' => SurveyDynamic#3(...)
        //         'iSurveyID' => 312499
        //         'surveyId' => 312499
        //     )
        // )
        //$oResponse = $this->getEvent()->get('model');
        //Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')), CLogger::LEVEL_INFO, 'application'); 
        // EXAMPLE_OUTPUT
        //2025/02/08 15:13:59 [info] [application] SurveyDynamic#1
        // (
        //     [CComponent:_e] => array
        //     (
        //         'onbeforesave' => CList#2
        //         (
        //             [CComponent:_e] => null
        //             [CComponent:_m] => null
        //             [CList:_d] => array
        //             (
        //                 0 => array
        //                 (
        //                     0 => CTimestampBehavior#3
        //                     (
        //                         [CComponent:_e] => null
        //                         [CComponent:_m] => null
        //                         [CBehavior:_enabled] => true
        //                         [CBehavior:_owner] => SurveyDynamic#1(...)
        //                         [createAttribute] => null
        //                         [updateAttribute] => null
        //                         [setUpdateOnCreate] => false
        //                         [timestampExpression] => CDbExpression#4
        //                         (
        //                             [CComponent:_e] => null
        //                             [CComponent:_m] => null
        //                             [expression] => 'NOW()'
        //                             [params] => array()
        //                         )
        //                     )
        //                     1 => 'beforeSave'
        //                 )
        //                 1 => array
        //                 (
        //                     0 => PluginEventBehavior#5
        //                     (
        //                         [CComponent:_e] => null
        //                         [CComponent:_m] => null
        //                         [CBehavior:_enabled] => true
        //                         [CBehavior:_owner] => SurveyDynamic#1(...)
        //                     )
        //                     1 => 'beforeSave'
        //                 )
        //             )
        //             [CList:_c] => 2
        //             [CList:_r] => false
        //         )
        //         'onafterdelete' => CList#6
        //         (
        //             [CComponent:_e] => null
        //             [CComponent:_m] => null
        //             [CList:_d] => array
        //             (
        //                 0 => array
        //                 (
        //                     0 => PluginEventBehavior#5(...)
        //                     1 => 'afterDelete'
        //                 )
        //             )
        //             [CList:_c] => 1
        //             [CList:_r] => false
        //         )
        //         'onaftersave' => CList#7
        //         (
        //             [CComponent:_e] => null
        //             [CComponent:_m] => null
        //             [CList:_d] => array
        //             (
        //                 0 => array
        //                 (
        //                     0 => PluginEventBehavior#5(...)
        //                     1 => 'afterSave'
        //                 )
        //             )
        //             [CList:_c] => 1
        //             [CList:_r] => false
        //         )
        //         'onbeforedelete' => CList#8
        //         (
        //             [CComponent:_e] => null
        //             [CComponent:_m] => null
        //             [CList:_d] => array
        //             (
        //                 0 => array
        //                 (
        //                     0 => PluginEventBehavior#5(...)
        //                     1 => 'beforeDelete'
        //                 )
        //             )
        //             [CList:_c] => 1
        //             [CList:_r] => false
        //         )
        //     )
        //     [CComponent:_m] => array
        //     (
        //         'CTimestampBehavior' => CTimestampBehavior#3(...)
        //         'PluginEventBehavior' => PluginEventBehavior#5(...)
        //     )
        //     [CModel:_errors] => array()
        //     [CModel:_validators] => null
        //     [CModel:_scenario] => 'insert'
        //     [CActiveRecord:_new] => true
        //     [CActiveRecord:_attributes] => array
        //     (
        //         'startlanguage' => 'de'
        //         'datestamp' => '2025-02-08 15:13:59'
        //         'startdate' => '2025-02-08 15:13:59'
        //         'seed' => '1757078866'
        //     )
        //     [CActiveRecord:_related] => array()
        //     [CActiveRecord:_c] => null
        //     [CActiveRecord:_pk] => null
        //     [CActiveRecord:_alias] => 't'
        //     [*:xssFilterAttributes] => array()
        //     [bEncryption] => false
        //     [completed_filter] => null
        //     [firstname_filter] => null
        //     [participant_id_filter] => null
        //     [lastname_filter] => null
        //     [email_filter] => null
        //     [lastpage] => null
        //     [*:bHaveToken] => null
        // )
        // $this->beforeSurveyDynamicSaveAddition(); // LETS DO ALL THE STUFF HERE

        // $oResponse = $this->getEvent()->get('model'); 
        // Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing():  Class of $oResponse: ' . get_class($oResponse), CLogger::LEVEL_INFO, 'application');
        // get_class($oResponse) is SurveyDynamic
        $surveyDynamicObject = $this->getEvent()->get('model'); 
        Yii::app()->session['surveyDynamicObject'] = $surveyDynamicObject;

        //Yii::log("ASDJASDHAHDASHDAHDASD",CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oResponse->attributes),CLogger::LEVEL_INFO, 'application');

        // $oResponse->attributes['participant_id'] = 999999999;  
        //Yii::log(CVarDumper::dumpAsString($oResponse->attributes),CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oResponse->attributes['seed']),CLogger::LEVEL_INFO, 'application');
        // Yii::log(CVarDumper::dumpAsString($oResponse->attributeNames()),CLogger::LEVEL_INFO, 'application');
        // array
        // (
        //     0 => 'id'
        //     1 => 'token'
        //     2 => 'participant_id'
        //     3 => 'submitdate'
        //     4 => 'lastpage'
        //     5 => 'startlanguage'
        //     6 => 'seed'
        //     7 => 'startdate'
        //     8 => 'datestamp'
        //     9 => '211297X8X258'
        // )
        //Yii::log(CVarDumper::dumpAsString($oResponse->getAttribute('participant_id')),CLogger::LEVEL_INFO, 'application');
        // $oResponse->setAttribute('participant_id',916123);
        // $oResponse->save(false)
        //$oResponse->save();
        //$oResponse->saveAttributes($oResponse->getAttributes());
        //Yii::log(CVarDumper::dumpAsString($oResponse->getAttribute('participant_id')),CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oResponse->getParticipantID()),CLogger::LEVEL_INFO, 'application');
        
        
        //Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing(): Updated attributes: ' . CVarDumper::dumpAsString($oResponse->attributes), CLogger::LEVEL_INFO, 'application');
        // if ($oResponse->save()) {
        //     Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing(): Participant ID saved successfully', CLogger::LEVEL_INFO, 'application');
        // } else {
        //     Yii::log('PraDiSy beforeSurveyDynamicSave Event called responseProcessing(): Failed to save participant ID: ' . CVarDumper::dumpAsString($oResponse->getErrors()), CLogger::LEVEL_ERROR, 'application');
        // }

        // $oResponse->attributes = array
        // (
        //     'startlanguage' => 'de'
        //     'token' => 't6WDHF8ezbrO6Db'
        //     'datestamp' => '2024-09-25 07:03:29'
        //     'startdate' => '2024-09-25 07:03:29'
        //     'seed' => '844391282'
        //     'id' => null
        //     'participant_id' => null
        //     'submitdate' => null
        //     'lastpage' => null
        //     '211297X8X258' => null
        // )


        // array (
        //     'startlanguage' => 'de'
        //     'token' => 't6WDHF8ezbrO6Db'
        //     'datestamp' => '2024-09-24 17:58:54'
        //     'startdate' => '2024-09-24 17:58:54'
        //     'seed' => '719040020'
        //     'id' => null
        //     'participant_id' => null
        //     'submitdate' => null
        //     'lastpage' => null
        //     '211297X8X258' => null
        // )
        //$oResponse->attributes['participant_id'] = '123456789';
        //$oResponse->save();
        //$oResponse->participant_id = '123456';
        //$this->getParticipantIdFromToken($token);
        //ERROR Yii::log(CVarDumper::dumpAsString($this->getParticipantIdFromToken($token)), CLogger::LEVEL_INFO, 'application'); 

        // MySQL ADDITIONS
        //$sTableName = Yii::app()->db->tablePrefix . 'survey_' . $iSurveyID;


    } // ADDED django0 because of https://manual.limesurvey.org/Dynamic_model_events#responseProcessing

    /*************  ✨ Codeium Command ⭐  *************/
        /**
         * BeforeSurveyDynamicSaveAddition event handler.
         * 
         * No function within the plugin just for debugging purposes.
         * This event is triggered before saving a SurveyDynamic response.
         * The handler retrieves the SurveyDynamic model from the event, checks
         * if the 'participant_id' attribute is missing, and if so, attempts to
         * retrieve it from another source (e.g. token). If the participant_id
         * is found, it is added to the SurveyDynamic model.
         */
    /******  18fbda59-5100-40b5-9a43-684cba5d9cc7  *******/ 
    public function beforeSurveyDynamicSaveAddition()
    {
        // Retrieve the SurveyDynamic model from the event
        $oResponse = $this->getEvent()->get('model');
        
        // Check if 'participant_id' exists in attributes array
        if (!array_key_exists('participant_id', $oResponse->attributes) || empty($oResponse->attributes['participant_id'])) {
            
            // Retrieve participant_id from token or another source
            // $token = $oResponse->attributes['token'];  // Assuming you have token stored in the attributes
            // Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
            // Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
            //$participantId = $this->getParticipantIdFromToken($token);
            
            // If we found a valid participant_id, set it in the model
            // if ($participantId !== null) {
            //     //$oResponse->participant_id = $participantId;
            //     $oResponse->participant_id = 123456789;
            //     Yii::log('Participant ID added to SurveyDynamic: ' . $participantId, CLogger::LEVEL_INFO, 'application');
            // } else {
            //     Yii::log('Could not find participant ID for token: ' . $token, CLogger::LEVEL_WARNING, 'application');
            // }
        }
        
        // Optionally, log the updated attributes
        //Yii::log('beforeSurveyDynamicSave - Attributes: ' . CVarDumper::dumpAsString($oResponse->attributes), CLogger::LEVEL_INFO, 'application');
    }
    

    /*************  ✨ Codeium Command ⭐  *************/
        /**
         * beforeResponseSaveProcedure.
         *
         * This event is triggered before saving a Response. Just for debugging purposes.
         * The handler retrieves the Response model from the event, checks
         * if the 'participant_id' attribute is missing, and if so, attempts to
         * retrieve it from another source (e.g. token). If the participant_id
         * is found, it is added to the Response model.
         *
         * @return void
         */
    /******  0694c669-5944-4553-b94c-ba4c43e41205  *******/ 
    public function beforeResponseSaveProcedure()
    {   
        Yii::log('PraDiSy beforeResponseSave Event called beforeResponseSaveProcedure(): ' 
        . ' File: ' . __FILE__ 
        . ' Line: ' . __LINE__ 
        . ' Function: ' . __FUNCTION__,
        CLogger::LEVEL_INFO, 
        'application');
        Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
        Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')), CLogger::LEVEL_INFO, 'application'); 

    //     $surveyId = $this->getEvent()->get('surveyId');
    //     if (empty($surveyId)) {
    //         // Something strange happen
    //     } else {
    //         // Log it somewhere
    //         //$oResponse = $this->getEvent()->get('model');
    //         //$this->log($oResponse->id." updated in survey".$surveyId);
    //         // Yii::log('PraDiSy beforeResponseSave() called: ' 
    //         //     . ' File: ' . __FILE__ 
    //         //     . ' Line: ' . __LINE__ 
    //         //     . ' Function: ' . __FUNCTION__
    //         //     . ' Attributes' = $oResponse->attributes,
    //         //     CLogger::LEVEL_INFO, 
    //         //     'application');
    //         //Yii::log('PraDiSy beforeResponseSave()', CLogger::LEVEL_INFO, 'application');
    //         // Yii::log(CVarDumper::dumpAsString($oResponse->attributes), CLogger::LEVEL_INFO, 'application');

    //         if ($oResponse->attributes['participant_id'] == null) {
    //             $oResponse->attributes['participant_id'] = 'jummy';   
    //         }
    //         //Yii::log(CVarDumper::dumpAsString($oResponse), CLogger::LEVEL_INFO, 'application');
    //         // Yii::log(CVarDumper::dumpAsString($oResponse->attributes['participant_id']), CLogger::LEVEL_INFO, 'application');
    //     }
    }

    // public function afterResponseSave()
    // {   
    //     // $surveyId = $this->getEvent()->get('surveyId');
    //     // if (empty($surveyId)) {
    //     //     Yii::log('PraDiSy afterResponseSave(): ERROR NO SURVEY ID FOUND', CLogger::LEVEL_INFO, 'application');
    //     //     Yii::log(CVarDumper::dumpAsString($oResponse), CLogger::LEVEL_INFO, 'application');
    //     // } else {
    //     //     // Log it somewhere
    //     //     $oResponse = $this->getEvent()->get('model');
    //     //     $this->log($oResponse->id." updated in survey".$surveyId);
    //     //     Yii::log('PraDiSy afterResponseSave(): ' . $surveyId, CLogger::LEVEL_INFO, 'application');
    //     //     Yii::log('PraDiSy afterResponseSave(): ' . $oResponse->id." updated in survey".$surveyId, CLogger::LEVEL_INFO, 'application');
    //     //     Yii::log(CVarDumper::dumpAsString($oResponse), CLogger::LEVEL_INFO, 'application');
    //     // }
    // }
    // public function responseProcessing() 
    // {
    //     Yii::log("CAlled responseProcessing()", CLogger::LEVEL_INFO, 'application');   
    // }

    /*************  ✨ Codeium Command ⭐  *************/
        /**
         * Checks if an array is associative.
         * 
         * Helper function. Just for debugging purposes. An array is considered associative if its keys are not 
         * consecutive numerical values. 
         * 
         * @param array $array The array to check.
         * @return boolean True if the array is associative, false otherwise.
         */
    /******  d0751da6-84c4-40d6-b3f8-dde2dc339427  *******/ 
    public function is_associative_array($array) 
    {
        // Prüft, ob das Array numerisch fortlaufende Schlüssel hat
        if (array_keys($array) !== range(0, count($array) - 1)) {
            return true; // Das Array ist assoziativ
        }
        return false; // Das Array ist numerisch
    }

    /*************  ✨ Codeium Command ⭐  *************/
        /**
         * Changes the length of the participant_id column in the given survey's response table to VARCHAR(36).
         *  Helper function to manipulate the database.
         * 
         * @param int $surveyId The ID of the survey to change.
         * @return void
         */
    /******  10ddb33a-27b7-4648-9b2b-155a76a563dd  *******/
    public function updateParticipantIdColumn($surveyId)
    {
        // Hole den dynamischen Tabellennamen
        $responseTable = $this->pluginManager->getAPI()->getResponseTable($surveyId);
    
        // SQL-Abfrage zum Ändern der Länge von participant_id
        $sql = "ALTER TABLE {$responseTable} MODIFY participant_id VARCHAR(36)";
    
        // Ausführen der SQL-Abfrage
        try {
            Yii::app()->db->createCommand($sql)->execute();
            Yii::log("Spalte participant_id erfolgreich auf VARCHAR(36) geändert für Tabelle {$responseTable}", CLogger::LEVEL_INFO, 'application');
        } catch (Exception $e) {
            Yii::log("Fehler beim Ändern der Spalte participant_id: " . $e->getMessage(), CLogger::LEVEL_ERROR, 'application');
        }
    }

    public function showTheResponse() 
    {
        // Yii::log('\n\n 1 \n\n' . CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
        if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
        {
            Yii::log('PraDiSy afterSurveyComplete Event called: showTheResponse(): ' 
                . ' File: ' . __FILE__ 
                . ' Line: ' . __LINE__ 
                . ' Function: ' . __FUNCTION__,
                CLogger::LEVEL_INFO, 
                'application');
            // more paranoid debugging
            // Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
            // Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')), CLogger::LEVEL_INFO, 'application'); //null
                    
        }else{
            
        }    

        // Yii::log(CVarDumper::dumpAsString($this->getEvent()),CLogger::LEVEL_INFO, 'application');
        $event      = $this->getEvent();
        // Yii::log("PIMIMIMI", CLogger::LEVEL_INFO, 'application');
        // Yii::log(CVarDumper::dumpAsString($event), CLogger::LEVEL_INFO, 'application');
        // PluginEvent#1
        // (
        //     [*:_event] => 'afterSurveyComplete'
        //     [*:_content] => array()
        //     [*:_sender] => null
        //     [*:_stop] => false
        //     [*:_parameters] => array
        //     (
        //         'responseId' => '102'
        //         'surveyId' => 211297
        //     )
        // )
        $surveyId   = $event->get('surveyId');
        // Yii::log('PraDiSy afterSurveyComplete Event called: showTheResponse(): $surveyId' , CLogger::LEVEL_INFO, 'application');   
        // Yii::log(CVarDumper::dumpAsString($surveyId), CLogger::LEVEL_INFO, 'application');
        $responseId = $event->get('responseId');
        // Yii::log('PraDiSy afterSurveyComplete Event called: showTheResponse(): $responseId' , CLogger::LEVEL_INFO, 'application');   
        // Yii::log(CVarDumper::dumpAsString($responseId), CLogger::LEVEL_INFO, 'application');
        // $participantId = $this->event->get('token');  // Zugriff auf die token aber bleibt leer!!!
        // Yii::log('PraDiSy afterSurveyComplete Event called: showTheResponse(): $token' , CLogger::LEVEL_INFO, 'application');   
        // Yii::log(CVarDumper::dumpAsString($participantId), CLogger::LEVEL_INFO, 'application');
        //Yii::log("Participant ID 45: " . $participantId, 'info', 'application');
        $response   = $this->pluginManager->getAPI()->getResponse($surveyId, $responseId);
        // Yii::log(CVarDumper::dumpAsString($this->pluginManager->getAPI()->getResponseTable($surveyId)), CLogger::LEVEL_INFO, 'application');        
        // 'PraDiSy_survey_211297' DER MySQL Table
        //$this->getEvent()->get('model')->setAttribute('participant_id', 123123123);
        // $this->pluginManager->getAPI()->setFlash("asdasdasd");
        //Yii::log("RINDIMAKI", CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($response), CLogger::LEVEL_INFO, 'application');        
        // array
        // (
        //     'id' => 103
        //     'token' => 't6WDHF8ezbrO6Db'
        //     'participant_id' => null
        //     'submitdate' => '2024-09-25 08:32:22'
        //     'startlanguage' => 'de'
        //     'seed' => '80289553'
        //     'startdate' => '2024-09-25 08:32:20'
        //     'datestamp' => '2024-09-25 08:32:22'
        //     'Q00' => '3'
        //     'lastpage' => 1
        // )
        // Yii::log('Class of $response: ' . get_class($response), CLogger::LEVEL_INFO, 'application');

        // $surveyId = $this->event->get('surveyId');
        //$oSurvey = Survey::model()->findByPk($surveyId);
        // this will not work Writer::write($oSurvey);
        //Yii::log(CVarDumper::dumpAsString($oSurvey), CLogger::LEVEL_INFO, 'application');        

        // PraDiSyCOMMENT Yii::log('PraDiSy afterSurveyComplete Event called showTheResponse(): TIKITAKKA', CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($this->getEvent()->get('model')->attributes['participant_id']), CLogger::LEVEL_INFO, 'application');   
        //Yii::log(CVarDumper::dumpAsString($response['id']), CLogger::LEVEL_INFO, 'application');   


        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($this->pluginManager->getAPI()->getResponseTable($surveyId)), CLogger::LEVEL_INFO, 'application');   
        $responseTable = $this->pluginManager->getAPI()->getResponseTable($surveyId);
        $this->updateParticipantIdColumn($surveyId);
        // SQL-Abfrage: Hole den Eintrag für die id = $responseId;
        $sql = "SELECT * FROM {$responseTable} WHERE id = :id";
        $command = Yii::app()->db->createCommand($sql);
        $command->bindValue(":id", $responseId, PDO::PARAM_INT);
        // Ausführen der Abfrage und Abrufen der Daten
        
        $participantIdObject = null;
        // Yii::app()->session['participantIdObject']
        
        if(!is_null(Yii::app()->session['participantIdObject'])){
            $participantIdObject = Yii::app()->session['participantIdObject'];
            
            if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
            {
                Yii::log('PraDiSy afterSurveyComplete Event: Assigning participantIdObject via SQL to the response table', CLogger::LEVEL_INFO, 'application');
            }
        }else{
            Yii::log('PraDiSy afterSurveyComplete ERROR!!! Could not retrive Yii::app()->session["participantIdObject"]', CLogger::LEVEL_INFO, 'application');
        }

        $tokenObject = null;
        
        if(!is_null(Yii::app()->session['tokenObject'])){
            $tokenObject = Yii::app()->session['tokenObject'];
            
            if($this->get('debugging', null, null, $this->settings['debugging']['default'])) 
            {
                Yii::log('PraDiSy afterSurveyComplete Event: Assigning tokenObject via SQL to the response table', CLogger::LEVEL_INFO, 'application');
            }
        }else{
            Yii::log('PraDiSy afterSurveyComplete ERROR!!! Could not retrive Yii::app()->session["tokenObject"]', CLogger::LEVEL_INFO, 'application');
        }

        // Yii::log('PraDiSy afterSurveyComplete ZULUZULU' . $responseData['token'] . " f " .  $response['token'], CLogger::LEVEL_INFO, 'application');
        
        
        $responseData = $command->queryRow();
        // ALTER TABLE `PraDiSysurvey_489276` MODIFY participant_id VARCHAR(36);
        // Überprüfen, ob Daten vorhanden sind
        if ($responseData) {
            // PraDiSyCOMMENT Yii::log('RIMANE Daten für id = ' . $responseId .  ' erfolgreich abgerufen: ' . CVarDumper::dumpAsString($responseData), CLogger::LEVEL_INFO, 'application');

             if (is_null($responseData['participant_id'])) {
                 // PraDiSyCOMMENT Yii::log('Participant ID ist NULL, wird nun auf ' . $participantIdObject . ' gesetzt.', CLogger::LEVEL_INFO, 'application');
    
                 //         // Update-Abfrage, um participant_id auf $participantIdObject zu setzen
                 $updateSql = "UPDATE {$responseTable} SET participant_id = :participant_id WHERE id = :id";
                 $updateCommand = Yii::app()->db->createCommand($updateSql);
                 $updateCommand->bindValue(":participant_id", $participantIdObject, PDO::PARAM_STR);
                 $updateCommand->bindValue(":id", $responseId, PDO::PARAM_INT);
    
                 // Ausführen der Update-Abfrage
                if ($updateCommand->execute()) {
                    // PraDiSyCOMMENT  Yii::log('Participant ID für id = ' . $responseId . ' erfolgreich auf ' . $participantIdObject . ' gesetzt.', CLogger::LEVEL_INFO, 'application');
                } else {
                    Yii::log('PraDiSyAfterAction ERROR: Fehler beim Setzen des Participant ID für id = ' . $responseId . '.', CLogger::LEVEL_ERROR, 'application');
                }
            } else {
                Yii::log("PraDiSyAfterAction WARNING: Participant ID ist bereits gesetzt: " . $responseData['participant_id'], CLogger::LEVEL_INFO, 'application');
            }

    //         if (is_null($responseData['token'])) {
    //             Yii::log('tokenObject ist NULL, wird nun auf ' . $tokenObject . ' gesetzt.', CLogger::LEVEL_INFO, 'application');
   
    //    //         // Update-Abfrage, um participant_id auf $participantIdObject zu setzen
    //             $updateSql = "UPDATE {$responseTable} SET token = :token WHERE id = :id";
    //             $updateCommand = Yii::app()->db->createCommand($updateSql);
    //             $updateCommand->bindValue(":token", $tokenObject, PDO::PARAM_STR);
    //             $updateCommand->bindValue(":id", $responseId, PDO::PARAM_INT);
   
    //             // Ausführen der Update-Abfrage
    //            if ($updateCommand->execute()) {
    //                Yii::log('Token ID für id = ' . $responseId . ' erfolgreich auf ' . $tokenObject . ' gesetzt.', CLogger::LEVEL_INFO, 'application');
    //            } else {
    //                Yii::log('Fehler beim Setzen des Participant ID für id = ' . $responseId . '.', CLogger::LEVEL_ERROR, 'application');
    //            }
    //        } else {
    //            Yii::log("Participant ID ist bereits gesetzt: " . $responseData['participant_id'], CLogger::LEVEL_INFO, 'application');
    //        }


        } else {
            // PraDiSyCOMMENT Yii::log('RIMANE Kein Eintrag gefunden für id = '. $responseId .' in der Tabelle {' . $responseTable . '}', CLogger::LEVEL_ERROR, 'application');
        }

        $oSurvey = Survey::model()->findByPk($surveyId);
        //Yii::log('JUTTA', CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oSurvey->template), CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oSurvey->attributedescriptions), CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oSurvey->tokenAttributes), CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString($oSurvey->getLocalizedTitle()), CLogger::LEVEL_INFO, 'application');

        //Yii::log("FUCKINGTASTIC", CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($surveyId), CLogger::LEVEL_INFO, 'application');
        //Yii::log(CVarDumper::dumpAsString("fieldinfo"), CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log("FUCKINGTASTIC", CLogger::LEVEL_INFO, 'application');
        $response['participant_id']= $participantIdObject;         
        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($response), CLogger::LEVEL_INFO, 'application');
        
        $post_processing_str = 'Sie haben erfolgreich den Fragebogen/die Fragebogenbatterie: <strong>' . $oSurvey->getLocalizedTitle() . '</strong> bearbeitet.<p>'
        . '<br/>Bitte notieren sie sich Ihre ID: <strong style="color:red;">' . $response['participant_id']  . '</strong><p> und ihren Zugangscode: <strong style="color:red;">' . $tokenObject . '</strong><p>'
        . 'Ihre Daten werden nun verschlüsselt an unsers Praxis gesendet:<br/><pre>' . '</pre><p>' . 'Sie können das Fenster nun schließen!' 
        . '<br/><br/><button type="button" style="font-size:16px; padding:10px;" onclick="window.close();">Fenster schließen</button>';

        //. 'Ihre Daten werden nun verschlüsselt an unsers Praxis gesendet:<br/><pre>' . print_r($response, true) . '</pre><p>' . 'Sie können das Fenster nun schließen!' ;

        $event->getContent($this)->addContent($post_processing_str);

        //$event->getContent($this)->addContent('Ihre Daten werden nun verschlüsselt an unsers Praxis gesndet:<br/><pre>' . print_r($response, true) . '</pre><p><p>' . 'Bitte notieren sie sich Ihre ID: ' . $response['participant_id'] . ' und ihren Zugangscode: ' . $response['token'] . '<p>');
        //$tmp34 = $this->writer->write($oSurvey);
        //Yii::log(CVarDumper::dumpAsString($tmp34), CLogger::LEVEL_INFO, 'application');        
        
        $surveyDynamicObject = Yii::app()->session['surveyDynamicObject']; // Aus der Session abrufen

        if($surveyDynamicObject)
        {

            // PraDiSyCOMMENT Yii::log('CRAZYCRAZYCRAZYCRAZYCRAZYCRAZY', CLogger::LEVEL_INFO, 'application');  
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString(array_keys($surveyDynamicObject->metaData->columns)), CLogger::LEVEL_INFO, 'application');        
        }

        $standard_array_columns = array(
            'id',
            'token',
            'submitdate',
            'lastpage',
            'startlanguage',
            'participant_id',
            'seed',
            'startdate',
            'datestamp'
        );

        

        if(is_array(array_keys($surveyDynamicObject->metaData->columns)))
        {
            // PraDiSyCOMMENT Yii::log('NICENICENICENICE', CLogger::LEVEL_INFO, 'application');  
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($standard_array_columns), CLogger::LEVEL_INFO, 'application');        
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString(array_keys($surveyDynamicObject->metaData->columns)), CLogger::LEVEL_INFO, 'application');        
            // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString(array_diff(array_keys($surveyDynamicObject->metaData->columns),$standard_array_columns)), CLogger::LEVEL_INFO, 'application');        
        }
        
        //array_diff(array_keys($surveyDynamicObject->metaData->columns),$standard_array_columns))

        if($this->is_associative_array(array_diff(array_keys($surveyDynamicObject->metaData->columns),$standard_array_columns)))
        {
            // PraDiSyCOMMENT  Yii::log('FUKY1', CLogger::LEVEL_INFO, 'application');  
        }
        if($this->is_associative_array($standard_array_columns))
        {
            // PraDiSyCOMMENT  Yii::log('FUKY2', CLogger::LEVEL_INFO, 'application');  
        }

        

        // if($surveyDynamicObject){
        //     //Yii::log(CVarDumper::dumpAsString($surveyDynamicObject), CLogger::LEVEL_INFO, 'application');
        //     Yii::log(CVarDumper::dumpAsString(array_keys($surveyDynamicObject->metaData->columns)), CLogger::LEVEL_INFO, 'application');
        // }else{
        //     Yii::log('SHITCAVE', CLogger::LEVEL_INFO, 'application');
        // }
        
        // PraDiSyCOMMENT Yii::log('GUMGBA', CLogger::LEVEL_INFO, 'application');        
        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($surveyDynamicObject), CLogger::LEVEL_INFO, 'application');        
        //$surveyDynamicObject

        // Yii::log(CVarDumper::dumpAsString($response['startlanguage']), CLogger::LEVEL_INFO, 'application');        

        Yii::app()->loadHelper('admin/exportresults');
        $oExport = new ExportSurveyResultsService();
        $oFormattingOptions = new FormattingOptions();
        //$oFormattingOptions->aResponses = '1,2,3';
        $oFormattingOptions->aResponses = $responseId;
        $oFormattingOptions->answerFormat = "short"; // force answer codes
        $oFormattingOptions->selectedColumns = array('id','token','submitdate','participant_id', 'seed', 'startdate','datestamp','489276X1X1');
        $oFormattingOptions->selectedColumns = array_merge($standard_array_columns,array_keys($surveyDynamicObject->metaData->columns));
        $oFormattingOptions->output = 'file';
        //Yii::log(CVarDumper::dumpAsString($response->startlanguage), CLogger::LEVEL_INFO, 'application');
        //$oFormattingOptions->output = 'display';
        // PraDiSyCOMMENT  Yii::log('JUTTA ' . CVarDumper::dumpAsString($oFormattingOptions), CLogger::LEVEL_INFO, 'application');

        // $oSurvey = Survey::model()->findByPk($surveyId);
        // Yii::log('JUTTA', CLogger::LEVEL_INFO, 'application');
        // //Yii::log(CVarDumper::dumpAsString($oSurvey->template), CLogger::LEVEL_INFO, 'application');
        // //Yii::log(CVarDumper::dumpAsString($oSurvey->attributedescriptions), CLogger::LEVEL_INFO, 'application');
        // //Yii::log(CVarDumper::dumpAsString($oSurvey->tokenAttributes), CLogger::LEVEL_INFO, 'application');
        // Yii::log(CVarDumper::dumpAsString($oSurvey->getLocalizedTitle()), CLogger::LEVEL_INFO, 'application');
        //$oFiledMap = $oSurvey->fieldMap;
        //Yii::log(CVarDumper::dumpAsString($oSurvey->getTokenAttributes()), CLogger::LEVEL_INFO, 'application');

        //Yii::log(CVarDumper::dumpAsString($oSurvey->sid), CLogger::LEVEL_INFO, 'application');
        // $oFiledMap = createFieldMap($surveyId, 'full', true, false, 'de');
        //Yii::log(CVarDumper::dumpAsString(getSurveyInfo($iSurveyID)), CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log('\n CHICKCI \n' . CVarDumper::dumpAsString($response), CLogger::LEVEL_INFO, 'application');
        $response['token'] = $tokenObject;
        // PraDiSyCOMMENT Yii::log('\n CHICKCI \n ' . CVarDumper::dumpAsString($response), CLogger::LEVEL_INFO, 'application');
        viewHelper::disableHtmlLogging();
        $file = $oExport->exportResponses($surveyId,$response['startlanguage'],'csv',$oFormattingOptions,'');

        // $tokenObject = isset(Yii::app()->session['tokenObject']) ? Yii::app()->session['tokenObject'] : '';

        // PraDiSyCOMMENT Yii::log("FUCKINGTASTIC FILE", CLogger::LEVEL_INFO, 'application');         
        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($file), CLogger::LEVEL_INFO, 'application');
        
        $oldFilePath = $file;
        if (file_exists($oldFilePath)) 
        {
            // Define the new file path with a .civ extension
            $newFilePath = $oldFilePath . '.csv';
        
            // Rename the file
            if (rename($oldFilePath, $newFilePath)) {
                Yii::log('PraDiSyAfterAction: CSV-File renamed successfully to: ' . $newFilePath, CLogger::LEVEL_INFO, 'application');
            } else {
                Yii::log('PraDiSyAfterAction ERROR: Error renaming the CSV-Data file.', CLogger::LEVEL_ERROR, 'application');
            }
        } else {
            Yii::log('PraDiSyAfterAction ERROR: CSV-File does not exist: ' . $oldFilePath, CLogger::LEVEL_WARNING, 'application');
        }
        $this->updateCsvToken($newFilePath, $tokenObject);
        $this->updateCsvSurveyId($newFilePath, $surveyId);

        $datestamp = $response['datestamp']; 
        list($oDate, $oTime) = explode(' ', $datestamp);

        $mailFilePath = '/../../' . $newFilePath;

        $argumentsForMail = array('surveyId' => $surveyId, 'participantId' => $participantIdObject, 'date' => $oDate, 'time' => $oTime, 'datafile' => $mailFilePath);
        // PraDiSyCOMMENT Yii::log('LOGGGOGOGOGO:', CLogger::LEVEL_ERROR, 'application');
        // PraDiSyCOMMENT Yii::log(CVarDumper::dumpAsString($argumentsForMail), CLogger::LEVEL_INFO, 'application');
        // Hier schreit alles und nichts funktioniert
        $this->sendSurveyCompletionMail($argumentsForMail);
        // $this->debugSendMail();
        //Yii::app()->end();
        //Yii::log(CVarDumper::dumpAsString($file), CLogger::LEVEL_INFO, 'application');
        //return new BigFile($file, true, 'base64');
    }

    // Diese Methode wird ausgeführt, wenn das 'afterSurveyComplete'-Event ausgelöst wird
    public function afterSurveyComplete()
    {
        //$surveyId = $this->event->get('surveyId');
        //$participantId = $this->event->get('token'); // Hier holen wir die Token-Information
        //$this->sendSurveyCompletionMail($surveyId, $participantId);
    }

    public function debugSendMail()
    {
        Yii::log('PraDiSy DEBUG: Starte SMTP-Mail-Test...', CLogger::LEVEL_INFO, 'application');
    
        // SMTP-Konfiguration aus den Plugin-Einstellungen holen
        $smtpHost = 'smtp.strato.de'; // $this->get('host', null, null, $this->settings['host']['default']);
        $smtpUsername = 'pradisy@gemeinschaftspraxis-psychotherapie-erfurt.de'; // $this->get('username', null, null, $this->settings['username']['default']);
        $smtpPassword = '#IntroiboAdAltareDei#7'; // $this->get('password', null, null, $this->settings['password']['default']);
        $smtpPort = 465; // $this->get('port', null, null, $this->settings['port']['default']);
        $smtpEncryption = 'ssl'; // $this->get('encryption', null, null, $this->settings['encryption']['default']);
        $receiverEmail = 'diagnostik@gemeinschaftspraxis-psychotherapie-erfurt.de'; // $this->get('receiver', null, null, $this->settings['receiver']['default']);
    

        $smtpHost = $this->get('host', null, null, $this->settings['host']['default']);
        $smtpUsername = $this->get('username', null, null, $this->settings['username']['default']);
        $smtpPassword = $this->get('password', null, null, $this->settings['password']['default']);
        $smtpPort = $this->get('port', null, null, $this->settings['port']['default']);
        $smtpEncryption =  $this->get('encryption', null, null, $this->settings['encryption']['default']);
        $receiverEmail =  $this->get('receiver', null, null, $this->settings['receiver']['default']);

        Yii::log('PraDiSy DEBUG: SMTP-Konfiguration geladen.', CLogger::LEVEL_INFO, 'application');
    
        try {
            $mail = new PHPMailer(true);

            if ($debuggingFlag) {
                $mail->SMTPDebug = 2;  // Enable verbose debug output
            }

            $mail->isSMTP();
            $mail->Host = $smtpHost;
            $mail->SMTPAuth = true;
            $mail->Username = $smtpUsername;
            $mail->Password = $smtpPassword;
            $mail->SMTPSecure = $smtpEncryption;
            $mail->Port = $smtpPort;
    
            $mail->setFrom($smtpUsername, 'PraDiSy Debug Mailer');
            $mail->addAddress($receiverEmail);
    
            $mail->isHTML(true);
            $mail->Subject = 'PraDiSy DEBUG: Testmail';
            $mail->Body    = 'Dies ist eine Testmail, um den SMTP-Mailer zu prüfen.';
            $mail->AltBody = 'Dies ist eine Testmail, um den SMTP-Mailer zu prüfen.';
    
            Yii::log('PraDiSy DEBUG: Bereite den E-Mail-Versand vor...', CLogger::LEVEL_INFO, 'application');
    
            if ($mail->send()) {
                Yii::log('PraDiSy DEBUG: E-Mail erfolgreich gesendet an ' . $receiverEmail, CLogger::LEVEL_INFO, 'application');
            } else {
                Yii::log('PraDiSy DEBUG: Fehler beim Senden der E-Mail: ' . $mail->ErrorInfo, CLogger::LEVEL_ERROR, 'application');
            }
        } catch (Exception $e) {
            Yii::log('PraDiSy DEBUG: Ausnahmefehler beim E-Mail-Versand: ' . $e->getMessage(), CLogger::LEVEL_ERROR, 'application');
        }
    }
    

    public function updateCsvToken($csvFile, $tokenValue)
    {
        // Öffne die CSV-Datei zum Lesen
        if (($handle = fopen($csvFile, 'r')) !== false) {
            // Lese die Kopfzeile
            $header = fgetcsv($handle, 0, ';');
            // Lese die einzige Datenzeile
            $data = fgetcsv($handle, 0, ';');
            fclose($handle);
    
            // Finde den Index der Spalte "token" in der Kopfzeile
            $tokenIndex = array_search('token', $header);
            if ($tokenIndex === false) {
                Yii::log("PraDiSyAfterAction ERROR: Die Spalte 'token' wurde nicht gefunden in " . $csvFile, CLogger::LEVEL_ERROR, 'application');
                return false;
            }
    
            // Setze den neuen Token-Wert in der Datenzeile
            $data[$tokenIndex] = $tokenValue;
    
            // Öffne die Datei erneut zum Schreiben (Überschreiben)
            if (($handle = fopen($csvFile, 'w')) !== false) {
                // Schreibe den Header und die aktualisierte Datenzeile zurück
                fputcsv($handle, $header, ';');
                fputcsv($handle, $data, ';');
                fclose($handle);
                // PraDiSyCOMMENT Yii::log("CSV-Datei " . $csvFile . " wurde erfolgreich aktualisiert.", CLogger::LEVEL_INFO, 'application');
                return true;
            } else {
                // PraDiSyCOMMENT Yii::log("Fehler beim Öffnen der Datei zum Schreiben: " . $csvFile, CLogger::LEVEL_ERROR, 'application');
                return false;
            }
        } else {
            // PraDiSyCOMMENT Yii::log("Fehler beim Öffnen der Datei zum Lesen: " . $csvFile, CLogger::LEVEL_ERROR, 'application');
            return false;
        }
    }
    

    public function updateCsvSurveyId($csvFile, $surveyId)
    {
        // Versuche, die CSV-Datei zum Lesen zu öffnen
        if (($handle = fopen($csvFile, 'r')) !== false) {
            // Lese die Kopfzeile
            $header = fgetcsv($handle, 0, ';');
            
            // Lese alle Datenzeilen in ein Array
            $dataRows = [];
            while (($row = fgetcsv($handle, 0, ';')) !== false) {
                $dataRows[] = $row;
            }
            fclose($handle);
        } else {
            Yii::log("PraDiSyAfterAction ERROR: Fehler beim Öffnen der Datei zum Lesen: " . $csvFile, CLogger::LEVEL_ERROR, 'application');
            return false;
        }
        
        // Falls die Spalte "survey_id" noch nicht vorhanden ist, füge sie zur Kopfzeile hinzu
        if (array_search('survey_id', $header) === false) {
            $header[] = 'survey_id';
        }
        
        // Füge in jeder Datenzeile den Wert für survey_id hinzu
        foreach ($dataRows as &$row) {
            $row[] = $surveyId;
        }
        unset($row);
        
        // Schreibe die CSV-Datei wieder (Überschreiben)
        if (($handle = fopen($csvFile, 'w')) !== false) {
            // Schreibe den Header zurück
            fputcsv($handle, $header, ';');
            // Schreibe alle Datenzeilen
            foreach ($dataRows as $row) {
                fputcsv($handle, $row, ';');
            }
            fclose($handle);
            Yii::log("PraDiSyAfterAction ERROR: Die CSV-Datei wurde um die Spalte 'survey_id' ergänzt.", CLogger::LEVEL_INFO, 'application');
            return true;
        } else {
            Yii::log("PraDiSyAfterAction ERROR: Fehler beim Öffnen der Datei zum Schreiben: " . $csvFile, CLogger::LEVEL_ERROR, 'application');
            return false;
        }
    }
    

    /**
     * Send an email with a CSV file containing the completed survey data
     * @param array $args An associative array containing the following keys:
     *   - surveyId: The ID of the survey
     *   - participantId: The    participant ID of the respondent
     *   - date: The date when the survey was completed
     *   - time: The time when the survey was completed
     *   - datafile: The path to the CSV file containing the survey data
     * @return boolean True if the email was sent successfully, false otherwise
     */
    private function sendSurveyCompletionMail($args)
    {
        if (empty($args['surveyId']) || empty($args['participantId']) || empty($args['date']) || empty($args['time']) || empty($args['datafile'])) {
            Yii::log('PraDiSyAfterAction Fehler: Fehlende Argumente zum Senden der E-Mail. Übergebene Argumente: ' . json_encode($args), 'error');
            return false;  // Exit the function if required arguments are missing
        }

        $datafile = $args['datafile'];
        if (!file_exists($datafile) || !is_readable($datafile)) {
            Yii::log('PraDiSyAfterAction Fehler: Die Datei existiert nicht oder kann nicht gelesen werden: ' . $datafile, 'error');
            return false;  // Exit the function if the file doesn't exist or is not readable
        }
        // Read the CSV file content
        $csvContent = file_get_contents($datafile);

        // Optionally format the CSV content for HTML output (e.g., into a table)
        $csvFormatted = nl2br($csvContent);  // Converts newlines to <br> for HTML

        //https://www.yiiframework.com/doc/guide/2.0/en/tutorial-mailing
        //$mailer = Yii::app()->mailer;
        // Fetch email settings from the plugin's settings array
        $smtpHost = $this->get('host', null, null, $this->settings['host']['default']);
        $smtpUsername = $this->get('username', null, null, $this->settings['username']['default']);
        $smtpPassword = $this->get('password', null, null, $this->settings['password']['default']);
        $smtpPort = $this->get('port', null, null, $this->settings['port']['default']);
        $smtpEncryption = $this->get('encryption', null, null, $this->settings['encryption']['default']);
        $receiverEmail = $this->get('receiver', null, null, $this->settings['receiver']['default']);  // Praxis server email
        $debuggingFlag = $this->get('debugging', null, null, $this->settings['debugging']['default']);

        $mail = new PHPMailer(true);

        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE SMTP-Konfiguration:', CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE Host: ' . $smtpHost, CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE Port: ' . $smtpPort, CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE Username: ' . $smtpUsername, CLogger::LEVEL_INFO, 'application');
        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE smtpPassword: ' . $smtpPassword, CLogger::LEVEL_INFO, 'application');        
        // PraDiSyCOMMENT Yii::log('DEBUGGING LASAGNE Encryption: ' . $smtpEncryption, CLogger::LEVEL_INFO, 'application');
        
        try {
            // Debugging settings (optional)
            // PraDiSyCOMMENT if ($debuggingFlag) {
            // PraDiSyCOMMENT     $mail->SMTPDebug = 2;  // Enable verbose debug output
            // PraDiSyCOMMENT }

            // PraDiSyCOMMENT Yii::log('PASTAFARI SMTP: Initialisiere Mailer...', CLogger::LEVEL_INFO, 'application');
            // PraDiSyCOMMENT Yii::log('PASTAFARI SMTP: Setze Mailer auf isSMTP()...', CLogger::LEVEL_INFO, 'application');
        

            // Server settings
            $mail->isSMTP();                                    // Set mailer to use SMTP
            $mail->Host       = $smtpHost;                      // SMTP server from plugin settings
            Yii::log('SMTP: Host: ' . $mail->Host, CLogger::LEVEL_INFO, 'application');
            $mail->SMTPAuth   = true;                           // Enable SMTP authentication
            $mail->Username   = $smtpUsername;                  // SMTP username from settings
            $mail->Password   = $smtpPassword;                  // SMTP password from settings
            $mail->SMTPSecure = $smtpEncryption;                // Encryption type (ssl/tls)
            Yii::log('SMTPSecure: Port: ' . $mail->SMTPSecure, CLogger::LEVEL_INFO, 'application');

            $mail->Port       = $smtpPort;                      // TCP port from settings

            // Sender info
            $mail->setFrom($smtpUsername, 'PraDiSy System');     // The sender address, can be your email or system email
            $mail->addAddress($receiverEmail);                  // Send to the receiver email (Praxis server)

            $subject_msg = 'DIAG' . $args['surveyId'] . 'PARTICIPANT' . $args['participantId'] . 'DATE' . $args['date'] . 'TIME' . $args['time'];

            // Email content
            $mail->isHTML(true);                                // Set email format to HTML
            $mail->Subject = $subject_msg;
            
            $mail->Body    = 'Die Umfrage #' . $args['surveyId'] . ' wurde erfolgreich abgeschlossen. <br><br>' .
            'CSV-Inhalt:<br>' . $csvFormatted;  // HTML body includes CSV content
            $mail->AltBody = 'Die Umfrage #' . $args['surveyId'] . ' wurde erfolgreich abgeschlossen. CSV-Inhalt: ' . $csvContent;  // Plain text

            //PraDiSyCOMMENT Yii::log('SMTP: $mail->Body ...' . $mail->Body, CLogger::LEVEL_INFO, 'application');

            $mail->addAttachment($datafile); 

            Yii::log('PraDiSyAfterAction: SMTP ... Bereite E-Mail zum Senden vor...', CLogger::LEVEL_INFO, 'application');


            // Send the email
            if ($mail->send()) {
                Yii::log('PraDiSyAfterAction: E-Email erfolgreich an den Praxis-Server (' . $receiverEmail . ') gesendet', 'info');
            } else {
                Yii::log('PraDiSyAfterAction: E-Mail konnte nicht an den Praxis-Server gesendet werden. Fehler: ' . $mail->ErrorInfo, 'error');
            }

        } catch (Exception $e) {
            // Log the error if the email fails to send
            Yii::log("PraDiSyAfterAction: Nachricht konnte nicht gesendet werden. Fehler: {$mail->ErrorInfo}", 'error');
        }
        // $mailer->From = $this->get('host', null, null, $this->settings['host']['default']);
        // $mailer->FromName = 'Praxis Diagnostik System Gemeinschaftspraxis Langen und Ziervogel';
        // $mailer->AddAddress($this->get('receiver', null, null, $this->settings['receiver']['default']));  // Dein Server, der die E-Mails empfangen soll
        // $mailer->Subject = 'Survey Completed: ' . $surveyId;

        // $host = $this->get('host', null, null, $this->settings['host']['default']);
        // $username = $this->get('username', null, null, $this->settings['username']['default']);
        // $password = $this->get('password', null, null, $this->settings['password']['default']);
        // $port = $this->get('port', null, null, $this->settings['port']['default']);
        // $encryption = $this->get('encryption', null, null, $this->settings['encryption']['default']);
        
        // Yii::app()->mailer->Host = $host;
        // Yii::app()->mailer->Username = $username;
        // Yii::app()->mailer->Password = $password;
        // Yii::app()->mailer->Port = $port;
        // Yii::app()->mailer->SMTPSecure = $encryption;

        // // E-Mail-Inhalt mit Umfragedaten
        // $message = "Participant ID: " . $participantId . "\n";
        // $message .= "Survey ID: " . $surveyId . "\n";
        // // Du kannst hier weitere Daten hinzufügen, falls erforderlich
        // $mailer->Body = $message;

        // $message = Yii::$app->mailer->compose();

        // // attach file from local file system
        // $message->attach('/path/to/source/file.pdf');
        
        // // create attachment on-the-fly
        // $message->attachContent('Attachment content', ['fileName' => 'attach.txt', 'contentType' => 'text/plain']);

        // // Sende die E-Mail
        // if ($mailer->Send()) {
        //     Yii::log("Survey completion email sent successfully", CLogger::LEVEL_INFO, 'application');
        // } else {
        //     Yii::log("Failed to send survey completion email", CLogger::LEVEL_ERROR, 'application');
        // }
    }
}
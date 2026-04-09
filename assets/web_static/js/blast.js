function updateBlastDatabase(dropdownName){
    switch(dropdownName) {

        case 'prot_db1':
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db2').value = '';
        document.getElementById('nt_db3').value = '';
        break;

        case 'prot_db2':
        document.getElementById('prot_db1').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db2').value = '';
        document.getElementById('nt_db3').value = '';
        break;



        case 'prot_db3':
        document.getElementById('prot_db1').value = '';
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db2').value = '';
        document.getElementById('nt_db3').value = '';
        break;

        case 'prot_db4':
        document.getElementById('prot_db1').value = '';
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db2').value = '';
        document.getElementById('nt_db3').value = '';
        break;

        case 'nt_db1':
        document.getElementById('prot_db1').value = '';
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db2').value = '';
        document.getElementById('nt_db3').value = '';
        break;

        case 'nt_db2':
        document.getElementById('prot_db1').value = '';
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db3').value = '';
        break;

        case 'nt_db3':
        document.getElementById('prot_db1').value = '';
        document.getElementById('prot_db2').value = '';
        document.getElementById('curated').checked = false;
        document.getElementById('prot_db3').value = '';
        document.getElementById('prot_db4').value = '';
        document.getElementById('nt_db1').value = '';
        document.getElementById('nt_db2').value = '';
        break;
    }
}


$(document).ready(function() {

//     document.getElementById('prot_db1').value = 'UniProtKB';
//     document.getElementById('prot_db2').value = '';
//     document.getElementById('prot_db3').value = '';
//     document.getElementById('curated').checked = true;
//     document.getElementById('prot_db3').value = '';
//     document.getElementById('prot_db4').value = '';
//     document.getElementById('nt_db1').value = '';
//     document.getElementById('nt_db2').value = '';
//     document.getElementById('nt_db3').value = '';


    // click on Reset...
    $('input[type=reset][name=reset]').click(function(){
        $('input:text[name=Tax]').attr('disabled', false);
    });



    $('dd.help').hide();
    $('.exc_help_content').hide();

    // when (re-) loading the page
    if ( $('select[name=prot_db1]').val() == '' && $('select[name=prot_db2]').val() == '' && $('select[name=prot_db3]').val() == '' && $('select[name=prot_db4]').val() == '' && $('select[name=nt_db1]').val() == '' && $('select[name=nt_db2]').val() == '' && $('select[name=nt_db3]').val() == '' ) {
        $('select[name=prot_db1]').val('UniProtKB');
        $('input:checkbox[name=curated]').prop('checked', true);
    }

    $('[id^=prot_db]').change(function(event){
        if ( $('select[name=prot_db1]').val() == 'UniProtKB' ) {
            $('input:text[name=Tax]').attr('disabled', false);
        }
        else {
            $('input:text[name=Tax]').attr('disabled', true);
        }
    });

    $('[id^=nt_db]').change(function(event){
        if ( $('select[name=prot_db1]').val() == 'UniProtKB' ) {
            $('input:text[name=Tax]').attr('disabled', false);
        }
        else {
            $('input:text[name=Tax]').attr('disabled', true);
        }
    });

    $('#ex_button').click(function(){

         var url_for_ajax = '/blast/ex1.txt';

         if ($('textarea[name=seqString]').val() == '>P43070\nMQIKFLTTLATVLTSVAAMGDLAFNLGVKNDDGTCKDVSTFEGDLDFLKSHSKIIKTYAVSDCNTLQNLGPAAEAEGFQIQLGIWPNDDAHFEAEKEALQNYLPKISVSTIKIFLVGSEALYREDLTASELASKINDIKGLVKGIKGKNGKSYSSVPVGTVDSWDVLVDGASKPAIDAADVVYSNSFSYWQKNSQANASYSLFDDVMQALQTLQTAKGSTDIEFWVGETGWPTDGSSYGDSVPSVENAADQWQKGICALRAWGINVAVYEAFDEAWKPDTSGTSSVEKHWGVWQSDKTLKYSIDCKFN\n>CfEC12\nMKTSILAILAVAAGLAVADDIKLPDCANGCLNDGLQKAGCTRDNIKDCYCQKADVNSLVTCVSNNCKSQNDLLAAAQSAGQICPNGVGNNGQFGNIPGFPGNNNNNNGGGGQGGGQGGGNNGGNKGGN\n>PSTG_04849\nMLSNTLRFATVLACSLLSFSPAAIGQDVAGLPACATTCLASSLASSGKTCAQTDFACLCKNNDFIKANNDCYQKTCSVGDLKTAAGWGAKTCAAAGVQIAANGVNSAADGVNSAANSATTGLTGGNHTNSTTTPATIPATTATNNSTSSANSSPVNTNPQTPVRPSSAAAVSVETVKFFAIGSALVCSMWMI\n>AVR-Mgk1\nMWSKSTIVTSAALLLFNQAALVAARNCRIWQDMGSVWQEVVVVTPPVTVDIITKRHGAFSLFVPVGCGIRDTGGALRATETDDPW\n>LEMA_P049940.1\nMVIYLPLYLLVLGIATTTISQPHLLCACESGRRDGVDDTRTLKVVKGTGGRFVFSIYWTKAEGAPHEGNYAHAINGTITKKGTNIQAHDDGLIGGEEMNSLCPEHSTCFSPNLKAKSTHSCGPDGKYGCVSAWLSVNWEGQIQ\n>estExt\nMFLRHFCVSFAVFIMAVAAAEPAVLTQEEVFNTVIDKSPFLTVATTTIVWTQSPSITTTQAPLAVTDSS\n') {
             $('textarea[name=seqString]').val('');
             return true;
         }
         else {
             $('textarea[name=seqString]').val('>P43070\nMQIKFLTTLATVLTSVAAMGDLAFNLGVKNDDGTCKDVSTFEGDLDFLKSHSKIIKTYAVSDCNTLQNLGPAAEAEGFQIQLGIWPNDDAHFEAEKEALQNYLPKISVSTIKIFLVGSEALYREDLTASELASKINDIKGLVKGIKGKNGKSYSSVPVGTVDSWDVLVDGASKPAIDAADVVYSNSFSYWQKNSQANASYSLFDDVMQALQTLQTAKGSTDIEFWVGETGWPTDGSSYGDSVPSVENAADQWQKGICALRAWGINVAVYEAFDEAWKPDTSGTSSVEKHWGVWQSDKTLKYSIDCKFN\n>CfEC12\nMKTSILAILAVAAGLAVADDIKLPDCANGCLNDGLQKAGCTRDNIKDCYCQKADVNSLVTCVSNNCKSQNDLLAAAQSAGQICPNGVGNNGQFGNIPGFPGNNNNNNGGGGQGGGQGGGNNGGNKGGN\n>PSTG_04849\nMLSNTLRFATVLACSLLSFSPAAIGQDVAGLPACATTCLASSLASSGKTCAQTDFACLCKNNDFIKANNDCYQKTCSVGDLKTAAGWGAKTCAAAGVQIAANGVNSAADGVNSAANSATTGLTGGNHTNSTTTPATIPATTATNNSTSSANSSPVNTNPQTPVRPSSAAAVSVETVKFFAIGSALVCSMWMI\n>AVR-Mgk1\nMWSKSTIVTSAALLLFNQAALVAARNCRIWQDMGSVWQEVVVVTPPVTVDIITKRHGAFSLFVPVGCGIRDTGGALRATETDDPW\n>LEMA_P049940.1\nMVIYLPLYLLVLGIATTTISQPHLLCACESGRRDGVDDTRTLKVVKGTGGRFVFSIYWTKAEGAPHEGNYAHAINGTITKKGTNIQAHDDGLIGGEEMNSLCPEHSTCFSPNLKAKSTHSCGPDGKYGCVSAWLSVNWEGQIQ\n>estExt\nMFLRHFCVSFAVFIMAVAAAEPAVLTQEEVFNTVIDKSPFLTVATTTIVWTQSPSITTTQAPLAVTDSS\n');
             return true;
         }
        $.ajax({
            url: url_for_ajax,
            dataType: 'text',
            success : function (data) {
                $('textarea[name=seqString]').val(data);
            }
        });

    });

    

    //These functions are used to export results as txt or excel.
    $('#ex_export_txt_button').click(function(){

         //Do something here

    });

    $('#ex_export_excel_button').click(function(){

         //Do something here

    });
//     $('#help').find('dd.help').hide().end().find('dt.help').click(function() {
//         $(this).next().slideToggle();
//     });
    $('dt.help').click(function() {
        $(this).next('dd.help:first').slideToggle();
    });
    $('.exc_help').click(function() {
        $('.exc_help_content').slideToggle();
    });
});

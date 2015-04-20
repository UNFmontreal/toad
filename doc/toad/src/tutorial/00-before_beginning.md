# Running this tutorial for the first time

---

## Request an account at the UNF


For further information please contact Mathieu Desrosiers <br>

&nbsp;&nbsp;&nbsp;&nbsp;email: mathieu.desrosiers@criugm.qc.ca
&nbsp;&nbsp;&nbsp;&nbsp;phone: 514-340-3540 #4897


## Connect to server

MacOSX User

###Open a terminal
Open the finder and Go to: Applications -> Utility -> Terminal

###Connect to the remote server
Type into the terminal
    ```# ssh -Y usersname@stark.criugm.qc.ca
    ```

    ```# source /usr/local/toad/etc/unf-toad-config.sh
    ```

Connect and launch à un des serveurs de l’UNF (stark ou magma)



localhost:dwi mathieu$ unf2toad toad_dicom/*


---------------------------------------------
Please select the folder in which to find the Please choose a session to convert files:

 0.  None
 1.  suj01
 2.  suj02
Enter your choice [0-2]: Default None [0] :1
Please enter a subject name? Defaults suj01 :


---------------------------------------------
Please select the folder in which to find the Anatomical (T1--MPRAGE) files:

 0.  None
 1.  01-MPRAGE_12ch
 2.  02-DWI_64
 3.  03-B0_AP
 4.  04-B0_PA
Enter your choice [0-4]: Default None [0] :1


---------------------------------------------
Please select the folder in which to find the Diffusion weighted image (DWI - DTI) files:

 0.  None
 1.  01-MPRAGE_12ch
 2.  02-DWI_64
 3.  03-B0_AP
 4.  04-B0_PA
Enter your choice [0-4]: Default None [0] :2


---------------------------------------------
Please select the folder in which to find the B0 AP (anterior -> posterior) files:

 0.  None
 1.  01-MPRAGE_12ch
 2.  02-DWI_64
 3.  03-B0_AP
 4.  04-B0_PA
Enter your choice [0-4]: Default None [0] :3


---------------------------------------------
Please select the folder in which to find the B0 PA (posterior -> anterior) files:

 0.  None
 1.  01-MPRAGE_12ch
 2.  02-DWI_64
 3.  03-B0_AP
 4.  04-B0_PA
Enter your choice [0-4]: Default None [0] :4
Whould you like to change default prefix at the beginning of the filename? Actual are ...
	Anatomical (T1--MPRAGE) will be prefix: anat_
	Diffusion weighted image (DWI - DTI) will be prefix: dwi_
	B0 AP (anterior -> posterior) will be prefix: b0_ap_
	B0 PA (posterior -> anterior) will be prefix: b0_pa_


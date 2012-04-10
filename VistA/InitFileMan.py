;---------------------------------------------------------------------------
; Copyright 2011 The Open Source Electronic Health Record Agent
;
; Licensed under the Apache License, Version 2.0 (the "License");
; you may not use this file except in compliance with the License.
; You may obtain a copy of the License at
;
;     http://www.apache.org/licenses/LICENSE-2.0
;
; Unless required by applicable law or agreed to in writing, software
; distributed under the License is distributed on an "AS IS" BASIS,
; WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
; See the License for the specific language governing permissions and
; limitations under the License.
;---------------------------------------------------------------------------
;initialization -- turn match off to make comparisons more lenient
case match: off

;set the title
title: Initialize FileMan
logfile:<P1>

on error: $Exit
; set up a timer for 10 minutes (10*60*10), should be more than enough to finish
timer 6000

wait for:>
;switch to the right namespace
send: znspace "${NAMESPACE}"<CR>
wait for:${NAMESPACE}>
;---------------------------------------------------------------------
;- SECTION TO INIT FILEMAN
;---------------------------------------------------------------------
send:D ^DINIT<CR>
wait for:Initialize VA FileMan now?
send:YES<CR>
wait for:SITE NAME:
send:DEMO.OSEHRA.ORG<CR>
wait for:SITE NUMBER:
send:6161<CR>
wait for:Do you want to change the MUMPS OPERATING SYSTEM File?
send:NO<CR>
wait for:TYPE OF MUMPS SYSTEM YOU ARE USING
send:CACHE<CR>
wait for:${NAMESPACE}>
send:D ^ZUSET<CR>
wait for:Rename
send:YES<CR>
wait for:${NAMESPACE}>
$Exit:
    timer 0
    ; close the log file
    closelog
    ; exit the terminal
    terminate

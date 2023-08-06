rmdir /s /q bin

cd tracgenericclass
rmdir /s /q build 
rmdir /s /q dist 
rmdir /s /q TracGenericClass.egg-info

cd ..\tracgenericworkflow
rmdir /s /q build 
rmdir /s /q dist 
rmdir /s /q TracGenericWorkflow.egg-info

cd ..\sqlexecutor
rmdir /s /q build 
rmdir /s /q dist 
rmdir /s /q SQLExecutor.egg-info

cd ..\testman4trac
rmdir /s /q build 
rmdir /s /q dist 
rmdir /s /q TestManager.egg-info

cd ..

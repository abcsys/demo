.PHONY: thing rule
thing:
	aws iot create-thing \
    --thing-name "MyLightBulb" \
    --thing-type-name "LightBulb" \
    --attribute-payload '{"attributes": {"wattage":"75", "model":"123"}}'
	

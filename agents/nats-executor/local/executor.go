package local

import (
	"context"
	"log"
	"os/exec"
	"time"
)

func Execute(req ExecuteRequest, instanceId string) ExecuteResponse {
	// Execute the command with timeout
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(req.ExecuteTimeout)*time.Second)
	defer cancel()

	log.Printf("Executing command: %s with timeout: %d seconds", req.Command, req.ExecuteTimeout)
	cmd := exec.CommandContext(ctx, "sh", "-c", req.Command)
	output, err := cmd.CombinedOutput()
	response := ExecuteResponse{
		Output:     string(output),
		InstanceId: instanceId,
		Success:    err == nil && ctx.Err() != context.DeadlineExceeded,
	}

	if ctx.Err() == context.DeadlineExceeded {
		log.Printf("Command timed out")
	} else if err != nil {
		log.Printf("Command execution error: %v", err)
	} else {
		log.Printf("Command output: %s", output)
	}

	return response

}

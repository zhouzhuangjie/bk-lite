package ssh

import (
	"context"
	"github.com/melbahja/goph"
	"log"
	"time"
)

func Execute(req ExecuteRequest, instanceId string) ExecuteResponse {
	auth := goph.Password(req.Password)
	client, err := goph.New(req.User, req.Host, auth)

	if err != nil {
		log.Printf("Failed to create new SSH client: %v", err)
		return ExecuteResponse{InstanceId: instanceId, Success: false}
	}

	defer client.Close()

	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(req.ExecuteTimeout)*time.Second)
	defer cancel()

	out, err := client.RunContext(ctx, req.Command)
	if err != nil {
		if ctx.Err() == context.DeadlineExceeded {
			log.Printf("Command timed out")
		} else {
			log.Printf("Command execution error: %v", err)
		}
		return ExecuteResponse{
			Output:     string(out),
			InstanceId: instanceId,
			Success:    false,
		}
	}

	return ExecuteResponse{
		Output:     string(out),
		InstanceId: instanceId,
		Success:    true,
	}
}

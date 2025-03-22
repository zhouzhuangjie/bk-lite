package local

import (
	"log"
	"testing"
)

func TestExecute(t *testing.T) {
	req := ExecuteRequest{
		Command:        "top",
		ExecuteTimeout: 5,
	}
	instanceId := "test-instance"
	response := Execute(req, instanceId)
	log.Println(response)
}

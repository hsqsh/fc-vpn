package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/client-go/kubernetes"
	"k8s.io/client-go/rest"
	"k8s.io/client-go/tools/clientcmd"
)

// getClientSet initializes the Kubernetes client
func getClientSet() (*kubernetes.Clientset, error) {
    // Try in-cluster config first
    config, err := rest.InClusterConfig()
    if err != nil {
        // Fallback to kubeconfig file
		homeDir, _ := os.UserHomeDir()
		kubeconfig := filepath.Join(homeDir, ".kube", "config")// 替换为实际路径
        config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
        if err != nil {
            return nil, err
        }
    }
    return kubernetes.NewForConfig(config)
}

// homeDir returns the home directory of the current user
func homeDir() string {
    if h := flag.Lookup("home"); h != nil {
        return h.Value.String()
    }
    return filepath.Dir("/home/sihan")
}

func listPods(w http.ResponseWriter, r *http.Request) {
    clientset, err := getClientSet()
    if err != nil {
        http.Error(w, fmt.Sprintf("Failed to create Kubernetes client: %v", err), http.StatusInternalServerError)
        return
    }

    pods, err := clientset.CoreV1().Pods("").List(r.Context(), metav1.ListOptions{})
    if err != nil {
        http.Error(w, fmt.Sprintf("Failed to list pods: %v", err), http.StatusInternalServerError)
        return
    }

    response := make([]map[string]string, 0)
    for _, pod := range pods.Items {
        response = append(response, map[string]string{
            "name":   pod.Name,
            "status": string(pod.Status.Phase),
            "ip":     pod.Status.PodIP,
        })
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{"pods": response})
}

func listNodes(w http.ResponseWriter, r *http.Request) {
    clientset, err := getClientSet()
    if err != nil {
        http.Error(w, fmt.Sprintf("Failed to create Kubernetes client: %v", err), http.StatusInternalServerError)
        return
    }

    nodes, err := clientset.CoreV1().Nodes().List(r.Context(), metav1.ListOptions{})
    if err != nil {
        http.Error(w, fmt.Sprintf("Failed to list nodes: %v", err), http.StatusInternalServerError)
        return
    }

    response := make([]map[string]string, 0)
    for _, node := range nodes.Items {
        response = append(response, map[string]string{
            "name":   node.Name,
            "status": string(node.Status.Phase),
        })
    }

    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]interface{}{"nodes": response})
}

func main() {
    http.HandleFunc("/k8s/pods", listPods)
    http.HandleFunc("/k8s/nodes", listNodes)

    fmt.Println("Server is running on port 8080...")
    http.ListenAndServe(":8080", nil)
}
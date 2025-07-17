package main

import (
	"encoding/json"
	"fmt"
	"log"
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
		// Fallback to kubeconfig file for local development
		homeDir, err := os.UserHomeDir()
		if err != nil {
			return nil, fmt.Errorf("failed to get home directory: %v", err)
		}
		kubeconfig := filepath.Join(homeDir, ".kube", "config")
		config, err = clientcmd.BuildConfigFromFlags("", kubeconfig)
		if err != nil {
			return nil, fmt.Errorf("failed to load kubeconfig: %v", err)
		}
	}

	clientset, err := kubernetes.NewForConfig(config)
	if err != nil {
		return nil, fmt.Errorf("failed to create clientset: %v", err)
	}
	return clientset, nil
}

// healthHandler handles health check requests
func healthHandler(w http.ResponseWriter, r *http.Request) {
	// Simple health check
	if _, err := getClientSet(); err != nil {
		log.Printf("Health check failed: %v", err)
		http.Error(w, "Not healthy", http.StatusServiceUnavailable)
		return
	}
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
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
	// Simple startup check
	if _, err := getClientSet(); err != nil {
		log.Printf("Warning: Initial connection to Kubernetes failed: %v", err)
		// 不立即退出，让健康检查处理它
	}

	mux := http.NewServeMux()

	// 添加路由
	mux.HandleFunc("/healthz", healthHandler)
	mux.HandleFunc("/k8s/pods", listPods)
	mux.HandleFunc("/k8s/nodes", listNodes)

	// 配置服务器
	server := &http.Server{
		Addr:    ":8080",
		Handler: mux,
	}

	// 启动服务器
	fmt.Println("Server is running on port 8080...")
	if err := server.ListenAndServe(); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

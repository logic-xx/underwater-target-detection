import { createRouter, createWebHistory } from "vue-router";

import HomeView from "../views/HomeView.vue";
import ImageDetectionView from "../views/ImageDetectionView.vue";
import VideoDetectionView from "../views/VideoDetectionView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/image",
      name: "image-detection",
      component: ImageDetectionView,
    },
    {
      path: "/video",
      name: "video-detection",
      component: VideoDetectionView,
    },
  ],
});

export default router;

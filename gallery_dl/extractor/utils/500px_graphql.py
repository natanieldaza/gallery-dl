# -*- coding: utf-8 -*-

# Copyright 2026 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.


getPhotoById = """\
query getPhotoById($id: ID!) {
  getPhotoById(id: $id) {
    id
    uploader {
      id
      avatar
      displayName
      isBlockedByMe
      username
      isFollowedByMe
      isFollowingMe
      membership {
        membership
        __typename
      }
      location
      city
      country
      state
      address
      __typename
    }
    title
    downloadable
    description
    uploadedAt
    uploadedLocation
    urls {
      size_600
      size_1024
      size_2048
      size_4k
      __typename
    }
    width
    height
    dominantColorLight
    dominantColorDark
    location
    locationText
    takenAt
    camera
    lens
    aperture
    focalLength
    shutterSpeed
    iso
    category
    techniques
    isNsfw
    isLikedByMe
    viewerHasReposted
    pulseScore
    viewCount
    likeCount
    favorCount
    commentCount
    hasComment
    shareCount
    repostCount
    geminiDetail {
      category
      style
      technique
      title
      keyword
      __typename
    }
    honors {
      __typename
      ... on PhotoHonorSelected {
        type
        __typename
      }
      ... on PhotoHonorAmbassadorsPick {
        ambassador {
          id
          avatar
          __typename
        }
        __typename
      }
      ... on PhotoHonorPxGallery {
        gallery {
          id
          name
          __typename
        }
        __typename
      }
    }
    needLoginToView
    aiArtAnalysis
    taggedAigc
    userDeclaredAigc
    isPrivate
    isInReview
    publicAiCritiqueReport {
      taskId
      status
      __typename
    }
    __typename
  }
}
"""

getVideoById = """\
query getVideoById($id: ID!) {
  getVideoById(id: $id) {
    id
    title
    description
    coverUrl
    videoUrl
    durationMs
    height
    uploadedAt
    commentCount
    favorCount
    isLikedByMe
    likeCount
    shareCount
    viewCount
    width
    locationText
    taggedAigc
    userDeclaredAigc
    isNsfw
    isInReview
    isPrivate
    isDeleted
    aiTrainingOptIn
    city
    country
    downloadable
    latitude
    location
    longitude
    poi
    privacy
    state
    honors {
      ...PhotoHonorFields
      __typename
    }
    uploader {
      id
      avatar
      displayName
      username
      isBlockedByMe
      isFollowedByMe
      isFollowingMe
      membership {
        membership
        __typename
      }
      location
      city
      country
      state
      address
      __typename
    }
    __typename
  }
}

fragment PhotoHonorFields on PhotoHonor {
  __typename
  ... on PhotoHonorSelected {
    type
    __typename
  }
  ... on PhotoHonorAmbassadorsPick {
    ambassador {
      id
      avatar
      __typename
    }
    __typename
  }
  ... on PhotoHonorPxGallery {
    gallery {
      id
      name
      __typename
    }
    __typename
  }
}
"""

getPhotoGroupById = """\
query getPhotoGroupById($id: ID!) {
  getPhotoGroupById(id: $id) {
    id
    uploader {
      id
      avatar
      displayName
      isBlockedByMe
      username
      isFollowedByMe
      isFollowingMe
      membership {
        membership
        __typename
      }
      location
      city
      country
      state
      address
      __typename
    }
    title
    description
    createdAt
    cover {
      urls {
        size_600
        size_1024
        size_2048
        size_4k
        __typename
      }
      __typename
    }
    isLikedByMe
    viewerHasReposted
    viewCount
    likeCount
    favorCount
    commentCount
    shareCount
    isPrivate
    isInReview
    honors {
      ...PhotoHonorFields
      __typename
    }
    __typename
  }
}

fragment PhotoHonorFields on PhotoHonor {
  __typename
  ... on PhotoHonorSelected {
    type
    __typename
  }
  ... on PhotoHonorAmbassadorsPick {
    ambassador {
      id
      avatar
      __typename
    }
    __typename
  }
  ... on PhotoHonorPxGallery {
    gallery {
      id
      name
      __typename
    }
    __typename
  }
}
"""

getPhotosByGroupId = """\
query getPhotosByGroupId($groupId: ID!, $excludeNsfw: Boolean) {
  getPhotosByGroupId(groupId: $groupId, excludeNsfw: $excludeNsfw) {
    id
    title
    width
    height
    takenAt
    uploadedAt
    taggedAigc
    userDeclaredAigc
    urls {
      size_600
      size_1024
      size_2048
      size_4k
      __typename
    }
    isNsfw
    __typename
  }
}
"""

pageResources = """\
query pageResources($userId: ID!, $first: Int!, $after: String, $resourceTypes: [ResourceType!], $sort: ResourceSortOption = CREATED_AT_DESC, $excludeNsfw: Boolean) {
  pageResources(
    userId: $userId
    first: $first
    after: $after
    resourceTypes: $resourceTypes
    sort: $sort
    excludeNsfw: $excludeNsfw
  ) {
    totalCount
    edges {
      cursor
      node {
        __typename
        ...PageProfileResourcesPhotoFragment
        ...PageProfileResourcesPhotoGroupFragment
        ...PageProfileResourcesVideoFragment
      }
      __typename
    }
    pageInfo {
      hasNextPage
      endCursor
      __typename
    }
    __typename
  }
}

fragment PhotoHonorFields on PhotoHonor {
  __typename
  ... on PhotoHonorSelected {
    type
    __typename
  }
  ... on PhotoHonorAmbassadorsPick {
    ambassador {
      id
      avatar
      __typename
    }
    __typename
  }
  ... on PhotoHonorPxGallery {
    gallery {
      id
      name
      __typename
    }
    __typename
  }
}

fragment PageProfileResourcesPhotoFragment on Photo {
  id
  isDeleted
  isInReview
  isPrivate
  taggedAigc
  userDeclaredAigc
  questInfo {
    rewardQuestName
    __typename
  }
  honors {
    ...PhotoHonorFields
    __typename
  }
  title
  description
  downloadable
  takenAt
  uploadedAt
  licensing {
    status
    __typename
  }
  urls {
    size_600
    size_1024
    size_2048
    size_4k
    __typename
  }
  uploader {
    id
    username
    avatar
    displayName
    isBlockedByMe
    isFollowedByMe
    isFollowingMe
    __typename
  }
  isNsfw
  isLikedByMe
  viewerHasReposted
  width
  height
  dominantColorLight
  dominantColorDark
  hasComment
  __typename
}

fragment PageProfileResourcesPhotoGroupFragment on PhotoGroup {
  id
  isDeleted
  isInReview
  isPrivate
  honors {
    ...PhotoHonorFields
    __typename
  }
  title
  description
  numCount
  publicItemCount
  isLikedByMe
  isNsfw
  viewerHasReposted
  uploader {
    id
    username
    displayName
    avatar
    isFollowedByMe
    isFollowingMe
    isBlockedByMe
    __typename
  }
  coverPhotos(first: 5) {
    id
    urls {
      size_600
      size_1024
      size_2048
      size_4k
      __typename
    }
    __typename
  }
  __typename
}

fragment PageProfileResourcesVideoFragment on Video {
  id
  isDeleted
  isInReview
  isPrivate
  isProcessing
  taggedAigc
  userDeclaredAigc
  questInfo {
    rewardQuestName
    __typename
  }
  honors {
    ...PhotoHonorFields
    __typename
  }
  title
  coverUrl
  videoUrl
  width
  height
  isNsfw
  isLikedByMe
  uploader {
    id
    username
    avatar
    displayName
    isBlockedByMe
    isFollowedByMe
    isFollowingMe
    __typename
  }
  __typename
}
"""

GetGalleryById = """\
query GetGalleryById($id: ID!) {
  getGalleryById(id: $id) {
    buttonName
    id
    name
    description
    externalUrl
    isPrivate
    isNsfw
    isDeleted
    isLikedByMe
    viewerHasReposted
    itemCount
    updatedAt
    likeCount
    viewCount
    commentCount
    hasComment
    shareCount
    repostCount
    pulseScore
    photographers(first: 4) {
      totalCount
      edges {
        node {
          id
          avatar
          username
          __typename
        }
        __typename
      }
      __typename
    }
    kind
    creator {
      id
      avatar
      displayName
      username
      location
      isBlockedByMe
      isFollowedByMe
      isFollowingMe
      membership {
        membership
        __typename
      }
      __typename
    }
    background {
      id
      width
      height
      urls {
        size_600
        size_1024
        size_2048
        size_4k
        __typename
      }
      __typename
    }
    coverPhotos(first: 1) {
      id
      urls {
        size_600
        size_1024
        size_2048
        size_4k
        __typename
      }
      __typename
    }
    honors {
      __typename
      ... on PhotoHonorSelected {
        type
        __typename
      }
      ... on PhotoHonorAmbassadorsPick {
        ambassador {
          id
          avatar
          __typename
        }
        __typename
      }
      ... on PhotoHonorPxGallery {
        gallery {
          id
          name
          __typename
        }
        __typename
      }
    }
    __typename
  }
}
"""

PageGalleryItems = """\
query PageGalleryItems($galleryId: ID!, $first: Int!, $after: String, $excludeNsfw: Boolean) {
  pageGalleryItems(
    galleryId: $galleryId
    first: $first
    after: $after
    excludeNsfw: $excludeNsfw
  ) {
    edges {
      cursor
      node {
        ... on Photo {
          __typename
          id
          isDeleted
          questInfo {
            rewardQuestName
            __typename
          }
          honors {
            ...PhotoHonorFields
            __typename
          }
          title
          licensing {
            status
            __typename
          }
          isPrivate
          isInReview
          isLikedByMe
          isNsfw
          viewerHasReposted
          likeCount
          viewCount
          width
          height
          takenAt
          uploadedAt
          uploader {
            id
            username
            avatar
            displayName
            isBlockedByMe
            isFollowedByMe
            isFollowingMe
            membership {
              membership
              __typename
            }
            __typename
          }
          urls {
            size_600
            size_1024
            size_2048
            size_4k
            __typename
          }
        }
        ... on PhotoGroup {
          __typename
          id
          isDeleted
          honors {
            ...PhotoHonorFields
            __typename
          }
          title
          description
          numCount
          publicItemCount
          isPrivate
          isInReview
          isLikedByMe
          isNsfw
          viewerHasReposted
          likeCount
          viewCount
          uploader {
            id
            username
            avatar
            displayName
            isBlockedByMe
            isFollowedByMe
            isFollowingMe
            membership {
              membership
              __typename
            }
            __typename
          }
          coverPhotos(first: 4) {
            id
            width
            height
            urls {
              size_600
              size_1024
              size_2048
              size_4k
              __typename
            }
            __typename
          }
        }
        ... on Video {
          __typename
          id
          isDeleted
          isInReview
          isPrivate
          questInfo {
            rewardQuestName
            __typename
          }
          honors {
            ...PhotoHonorFields
            __typename
          }
          title
          coverUrl
          videoUrl
          width
          height
          isNsfw
          isLikedByMe
          uploader {
            id
            username
            avatar
            displayName
            isBlockedByMe
            isFollowedByMe
            isFollowingMe
            membership {
              membership
              __typename
            }
            __typename
          }
        }
        __typename
      }
      __typename
    }
    pageInfo {
      endCursor
      hasNextPage
      hasPreviousPage
      __typename
    }
    __typename
  }
}

fragment PhotoHonorFields on PhotoHonor {
  __typename
  ... on PhotoHonorSelected {
    type
    __typename
  }
  ... on PhotoHonorAmbassadorsPick {
    ambassador {
      id
      avatar
      __typename
    }
    __typename
  }
  ... on PhotoHonorPxGallery {
    gallery {
      id
      name
      __typename
    }
    __typename
  }
}
"""

getUserProfile = """\
query getUserProfile($username: String!) {
  getUser(username: $username) {
    ...ProfileUserFields
    __typename
  }
}

fragment ProfileUserFields on User {
  id
  username
  displayName
  avatar
  cover
  about
  location
  level
  sex
  followeesCount
  followersCount
  likeCount
  publicResourceCount
  publicGalleryCount
  userStats {
    numQuestEntered
    __typename
  }
  isFollowedByMe
  isFollowingMe
  isBlockedByMe
  userType
  membership {
    membership
    __typename
  }
  contacts {
    id
    type
    contact
    visible
    __typename
  }
  coverPhotos(first: 4) {
    id
    urls {
      size_600
      size_1024
      size_2048
      size_4k
      __typename
    }
    __typename
  }
  profileTabs(isMobile: false) {
    id
    tab
    visible
    __typename
  }
  __typename
}
"""
